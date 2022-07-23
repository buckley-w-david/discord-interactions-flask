"""
Main extension module.

This is the primary interaction point, a user will define their commands using an instance of the :class:`Discord` class.
"""


from collections import defaultdict
import http
import json
import logging
from typing import Optional, Union, Iterable

from flask import Blueprint, Flask, jsonify, request

import urllib3

from discord_interactions_flask import discord_types as types
from discord_interactions_flask.verify import verify_key_decorator
from discord_interactions_flask.command_builder import CommandBuilder
from discord_interactions_flask.command import Command
from discord_interactions_flask import errors
from discord_interactions_flask.interactions import (
    ChatInteraction,
    UserInteraction,
    MessageInteraction,
    ButtonInteraction,
    SelectMenuInteraction,
    TextInputInteraction,
    ComponentInteraction,
    CommandInteraction,
)
from discord_interactions_flask import helpers
from discord_interactions_flask import components

logger = logging.getLogger(__name__)

GLOBAL_URL_TEMPLATE = "https://discord.com/api/v10/applications/%s/commands"
GUILD_URL_TEMPLATE = "https://discord.com/api/v10/applications/%s/guilds/%s/commands"
OAUTH_ENDPOINT = "https://discord.com/api/v10/oauth2/token"


def _missing_component_handler(
    _: ComponentInteraction,
) -> types.InteractionResponse:
    resp = helpers.content_response(
        ":warning: Sorry, that component has expired! :warning:",
        flags=types.MessageFlags.EPHEMERAL,
    )
    return resp


def _missing_command_handler(
    _: CommandInteraction,
) -> types.InteractionResponse:
    resp = helpers.content_response(
        ":warning: Sorry, I don't understand that command! :warning:",
        flags=types.MessageFlags.EPHEMERAL,
    )
    return resp


class Discord:
    """Creates :class:`Command` s, submits them to the configured Discord application, and recieves the HTTP requests."""

    def __init__(
        self,
        app: Optional[Flask] = None,
        missing_command_handler=_missing_command_handler,
        missing_component_handler=_missing_component_handler,
    ):
        """Initialzation."""

        # TODO: Would be nice if I didn't have to maintain two separate dicts of commands
        self.commands: defaultdict[Optional[str], dict[str, Command]] = defaultdict(dict)

        self.runtime_commands: dict[str, Command] = {}

        # TODO: evict old handlers
        self.component_handlers: defaultdict[
            str, dict[str, components.Component]
        ] = defaultdict(dict)

        self.missing_command_handler = missing_command_handler
        self.missing_component_handler = missing_component_handler
        self.http = urllib3.PoolManager(headers={"Content-Type": "application/json"})
        self.public_key = None
        if app:
            self.init_app(app)

    def command(
            self, name: Optional[str] = None, description: Optional[str] = None, guild_id: Optional[str] = None
    ) -> CommandBuilder:
        """Define a new command.

        Type hints on the argument types are used to build the correct Command.
        Check the examples to see the options.

        .. code-block:: python

            @discord.command()
            def command(interaction: interactions.ChatInteraction) -> types.InteractionResponse:
                return ...

        Args
            name: An optional name to give the command. If not given the function name will be used.
            description: An optional description to give the command. If not given the name will be used.
            guild_id: An optional guild_id. If given the command will be created in just that guild.

        Returns
            A :class:`CommandBuilder` instance that can be used as a decorator or context manager.
        """
        return CommandBuilder(self, name, description, guild_id)

    def _handle_response(
        self, interaction: types.Interaction, response: types.InteractionResponse
    ):
        if response.data and response.data.components:
            for row in response.data.components:
                for component in row.components:
                    self.component_handlers[interaction.id][
                        component.custom_id
                    ] = component

        return jsonify(
            response.dump(
                use_enum_name=False, strip_privates=True, strip_properties=True
            )
        )

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
            assert payload is not None

            match payload["type"]:
                case types.InteractionType.PING:
                    return jsonify(type=types.InteractionCallbackType.PONG)
                case types.InteractionType.APPLICATION_COMMAND:
                    command_interaction: Union[
                        ChatInteraction, UserInteraction, MessageInteraction
                    ]
                    match payload["data"]["type"]:
                        case types.CommandType.CHAT:
                            command_interaction = ChatInteraction.load(payload)
                        case types.CommandType.USER:
                            command_interaction = UserInteraction.load(payload)
                        case types.CommandType.MESSAGE:
                            command_interaction = MessageInteraction.load(payload)
                        case _:
                            raise errors.DiscordInteractionsFlaskError(
                                "Discord sent an invalid command type - %s"
                                % payload["data"]["type"]
                            )

                    handler = self.runtime_commands.get(command_interaction.data.id)
                    if not handler:
                        result = self.missing_command_handler(command_interaction)
                    else:
                        result = handler(command_interaction)

                    return self._handle_response(command_interaction, result)
                case types.InteractionType.MESSAGE_COMPONENT:
                    component_interaction: Union[
                        ButtonInteraction, SelectMenuInteraction, TextInputInteraction
                    ]
                    match payload["data"]["component_type"]:
                        case types.ComponentType.BUTTON:
                            component_interaction = ButtonInteraction.load(payload)
                        case types.ComponentType.SELECT_MENU:
                            component_interaction = SelectMenuInteraction.load(payload)
                        case types.ComponentType.TEXT_INPUT:
                            component_interaction = TextInputInteraction.load(payload)
                        case _:
                            raise errors.DiscordInteractionsFlaskError(
                                "Discord sent an invalid component type - %s"
                                % payload["data"]["type"]
                            )

                    # It's interesting that typing errors have pushed me to explicitly define my invariants
                    assert component_interaction.message is not None
                    assert component_interaction.message.interaction is not None

                    handlers = self.component_handlers.get(
                        component_interaction.message.interaction.id
                    )
                    if not handlers or component_interaction.data.custom_id not in handlers:
                        result = self.missing_component_handler(component_interaction)
                    else:
                        result = handlers[component_interaction.data.custom_id](component_interaction)

                    return self._handle_response(component_interaction, result)
                case _:
                    print("OTHER")
                    print(payload)
                    return ("", http.HTTPStatus.NO_CONTENT)

        app.register_blueprint(interactions_bp)
        self.init_commands(app)

    def _refresh_token(self):
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
        token = json.loads(r.data.decode("utf-8"))
        self.http.headers[
            "Authorization"
        ] = f"{token['token_type']} {token['access_token']}"

    def _create_commands(
        self, commands: Iterable[Command], guild_id: Optional[str] = None
    ) -> list[types.ApplicationCommand]:
        """Push the list of :class:`Command` to the Discord application indicated by the DISCORD_CLIENT_ID key in bulk.

        Args
            command: The command the create.
            guild_id: if not present, the command will be created as a global one. Otherwise it will be created for the specifiied guild.
        """
        if guild_id:
            url = GUILD_URL_TEMPLATE % (self.client_id, guild_id)
        else:
            url = GLOBAL_URL_TEMPLATE % self.client_id

        resp = self.http.request(
            "PUT", url, body=json.dumps([command.spec() for command in commands]).encode("utf-8")
        )
        if resp.status == http.HTTPStatus.OK:
            return [types.ApplicationCommand.load(payload) for payload in json.loads(resp.data.decode("utf-8"))]
        else:
            raise errors.DiscordApiError(resp.data.decode("utf-8"))

    def _create_command(
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
        if resp.status == http.HTTPStatus.OK or resp.status == http.HTTPStatus.CREATED:
            interaction_payload = json.loads(resp.data.decode("utf-8"))
            return types.ApplicationCommand.load(interaction_payload)
        else:
            raise errors.DiscordApiError(resp.data.decode("utf-8"))

    def add_command(
        self, name: str, command: Command, guild_id: Optional[str] = None
    ) -> None:
        self.commands[guild_id][name] = command

        # If we're already initialized, we send the command to discord right away
        if self.public_key is not None:
            interaction = self._create_command(command, guild_id)
            self.runtime_commands[interaction.id] = command

    def remove_command(
        self, interaction_id: str, guild_id: Optional[str] = None
    ) -> None:
        if guild_id:
            url = GUILD_URL_TEMPLATE % (self.client_id, guild_id)
        else:
            url = GLOBAL_URL_TEMPLATE % self.client_id

        url += f"/{interaction_id}"
        del self.runtime_commands[interaction_id]

        resp = self.http.request("DELETE", url)
        if resp.status != http.HTTPStatus.NO_CONTENT:
            raise errors.DiscordApiError(resp.data.decode("utf-8"))

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

        if not self.commands:
            logger.warning(
                "Running init_commands with no commands defined!\n"
                "If you would like discord-interactions-flask to automatically push commands to Discord you will "
                "need to run `init_commands` _after_ defining your commands",
                self,
            )
            return

        self._refresh_token()

        for guild_id, commands in self.commands.items():
            iteractions = self._create_commands(commands.values(), guild_id)

            for command, interaction in zip(commands.values(), iteractions):
                self.runtime_commands[interaction.id] = command
