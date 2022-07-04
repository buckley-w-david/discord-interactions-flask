"""
Main extension module.

This is the primary interaction point, a user will define their commands using an instance of the :class:`Discord` class.
"""


from collections import defaultdict
import json
import logging
from typing import Optional

from flask import Blueprint, Flask, jsonify, request

import urllib3

from flask_discord_interactions import discord_types as types
from flask_discord_interactions.verify import verify_key_decorator
from flask_discord_interactions.command_builder import CommandBuilder
from flask_discord_interactions.command import Command

logger = logging.getLogger(__name__)

GLOBAL_URL_TEMPLATE = "https://discord.com/api/v10/applications/%s/commands"
GUILD_URL_TEMPLATE = "https://discord.com/api/v10/applications/%s/guilds/%s/commands"
OAUTH_ENDPOINT = "https://discord.com/api/v10/oauth2/token"


class Discord:
    """Creates :class:`Command` s, submits them to the configured Discord application, and recieves the HTTP requests."""

    def __init__(self, app: Optional[Flask] = None):
        """Initialzation."""
        self.guild_commands = defaultdict(dict)
        self.global_commands = {}
        self.runtime_commands = {}
        self.http = urllib3.PoolManager(headers={"Content-Type": "application/json"})
        if app:
            self.init_app(app)

    def command(
        self, name: Optional[str] = None, guild_id: Optional[str] = None
    ) -> CommandBuilder:
        """Define a new command.

        Type hints on the argument types are used to build the correct Command.
        Check the examples to see the options.

        .. code-block:: python

            @discord.command()
            def command(interaction: types.ChatInteraction) -> types.InteractionResponse:
                return ...

        Args
            name: An optional name to give the command. If not given the function name will be used.
            guild_id: An optional guild_id. If given the command will be created in just that guild.

        Returns
            A :class:`CommandBuilder` instance that can be used as a decorator or context manager.
        """
        if guild_id:
            commands = self.guild_commands[guild_id]
        else:
            commands = self.global_commands
        return CommandBuilder(commands, name)

    def init_app(self, app: Flask) -> None:
        """Initialize the :class:`Flask` instance with all the commands defined on this :class:`Discord` instance.

        Args
            app: A :class:`Flask` instance. Must have the `DISCORD_PUBLIC_KEY`, `DISCORD_CLIENT_ID`, and `DISCORD_CLIENT_SECRET` configuration keys defined.
        """
        self.public_key = app.config.setdefault("DISCORD_PUBLIC_KEY", "")
        if not self.public_key:
            raise ValueError("You must define a DISCORD_PUBLIC_KEY configuration value")

        # TODO: I'd like to move the bp out of init_app, the verify_key_decorator makes it awkward since with it I need the public key at bp creation time
        interactions_bp = Blueprint("interactions", __name__, url_prefix="/discord")

        @interactions_bp.post("/interactions")
        @verify_key_decorator(self.public_key)
        def interactions():
            payload = request.json
            if not payload:
                raise

            match payload["type"]:
                case types.InteractionType.PING:
                    return jsonify(type=types.InteractionCallbackType.PONG)
                case types.InteractionType.APPLICATION_COMMAND:
                    match payload["data"]["type"]:
                        case types.CommandType.CHAT:
                            interaction = types.ChatInteraction.load(payload)
                        case types.CommandType.USER:
                            interaction = types.UserInteraction.load(payload)
                        case types.CommandType.MESSAGE:
                            interaction = types.MessageInteraction.load(payload)
                        case _:
                            raise ValueError("WTF Discord?")

                    result = self.runtime_commands[interaction.data.id](interaction)
                    if result:
                        return jsonify(result.dump(use_enum_name=False))
                case _:
                    pass

        app.register_blueprint(interactions_bp)
        self.init_commands(app)

    def refresh_token(self):
        """Refresh the OAuth2 client credentials used to interact with the Discord API. Typically not something a user is expected to need."""
        r = self.http.request(
            "POST",
            OAUTH_ENDPOINT,
            fields={
                "grant_type": "client_credentials",
                "scope": "applications.commands.update",
            },
            headers=urllib3.util.make_headers(
                basic_auth=f"{self.client_id}:{self.client_secret}"
            ),
            encode_multipart=False,
        )
        # r.raise_for_status()
        token = json.loads(r.data.decode("utf-8"))
        self.http.headers[
            "Authorization"
        ] = f"{token['token_type']} {token['access_token']}"

    def create_command(
        self, command: Command, guild_id: Optional[str] = None
    ) -> types.ApplicationCommand:
        """Push the :class:`Command` to the Discord application indicated by the DISCORD_CLIENT_ID key.

        Args
            command: The command the create.
            guild_id: if not present, the command will be created as a global one. Otherwise it will be created for the specifiied guild.
        """
        if guild_id:
            url = GUILD_URL_TEMPLATE % (self.client_id, guild_id)
        else:
            url = GLOBAL_URL_TEMPLATE % self.client_id

        resp = self.http.request(
            "POST", url, body=json.dumps(command.spec()).encode("utf-8")
        )
        interaction_payload = json.loads(resp.data.decode("utf-8"))
        return types.ApplicationCommand.load(interaction_payload)

    def init_commands(self, app: Flask):
        """Sync the :class:`Command` s configured with this :class:`Discord` instance to the Discord application indicated by the DISCORD_CLIENT_ID key.

        Args
            app: A :class:`Flask` instance configured with a `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET`
        """
        self.client_id = app.config.setdefault("DISCORD_CLIENT_ID", "")
        self.client_secret = app.config.setdefault("DISCORD_CLIENT_SECRET", "")

        if not (self.client_id and self.client_secret):
            raise ValueError(
                "You must define DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET configuration values"
            )

        if not self.guild_commands and not self.global_commands:
            logger.warning(
                "Running init_commands with no commands defined!\n"
                "If you would like flask-discord-interactions to automatically push commands to Discord you will "
                "need to run `init_commands` _after_ defining your commands",
                self,
            )
            return

        self.refresh_token()

        for (guild_id, commands) in self.guild_commands.items():
            for (_, command) in commands.items():
                interaction = self.create_command(command, guild_id)
                self.runtime_commands[interaction.id] = command

        for (_, command) in self.global_commands.items():
            interaction = self.create_command(command)
            self.runtime_commands[interaction.id] = command
