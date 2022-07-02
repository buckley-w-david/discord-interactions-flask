__version__ = '0.1.0'

# TODO: Your app can have a global CHAT_INPUT and USER command with the same name
#       Do I just decide to not support that?
#       I would have to break out each command type into separate dicts

from collections import defaultdict
from contextlib import contextmanager
import inspect
import json
import logging
from typing import Callable, Optional, Union

from flask import Blueprint, Flask, jsonify, request
# TODO: I think I could switch types to attrs and use cattrs for this
import jsons
import urllib3

from flask_discord_interactions import discord_types as types
from flask_discord_interactions.command import (
    ChatCommand,
    ChatMetaCommand,
    CommandGroup,
    MessageCommand,
    SubCommand,
    UserCommand,
)
from flask_discord_interactions.verify import verify_key_decorator

logger = logging.getLogger(__name__)



COMMANDS = {
    types.ChatInteraction: ChatCommand,
    types.UserInteraction: UserCommand,
    types.MessageInteraction: MessageCommand,
}

GLOBAL_URL_TEMPLATE = "https://discord.com/api/v10/applications/%s/commands"
GUILD_URL_TEMPLATE  = "https://discord.com/api/v10/applications/%s/guilds/%s/commands"
OAUTH_ENDPOINT      = 'https://discord.com/api/v10/oauth2/token'

# There is a term for why I need to specify the type like this instead of `Callable[[types.Interaction], types.InteractionResponse]` being able to apply to all three, I just forget what it is
# The rationale is that `Callable[[types.Interaction], types.InteractionResponse]` means "Function that can take any Interaction and returns an InteractionResponse"
# A function that can only take UserInteractions does not satisfy that
COMMAND_FUNCTION = Union[
    Callable[[types.ChatInteraction], types.InteractionResponse],
    Callable[[types.UserInteraction], types.InteractionResponse],
    Callable[[types.MessageInteraction], types.InteractionResponse],
]

# This is getting pretty big/complex, would be nice to break it up
class Discord:
    def __init__(self, app: Optional[Flask] = None):
        self.guild_commands = defaultdict(dict)
        self.global_commands = {}
        self.runtime_commands = {}
        if app:
            self.init_app(app)

    def command(self, outer_name: str, outer_guild: Optional[str] = None):
        guild_commands = self.guild_commands
        global_commands = self.global_commands
        # Very readable, good work David
        # Note to future me, this made perfect sense at the time
        # This is a kind of neat pattern though, I've never made anything that was simultaneously a decorator _and_ a context manager before
        class Builder:
            def __init__(self):
                self.context = { }

            def __call__(self, f: COMMAND_FUNCTION):
                if outer_guild:
                    commands = guild_commands[outer_guild]
                else:
                    commands = global_commands
                signature = inspect.signature(f)
                param = list(signature.parameters.values())[0]
                if not (command_class := COMMANDS.get(param.annotation)):
                    raise ValueError("Command parameter must be a valid Interaction type")
                command = command_class(outer_name, f)
                commands[outer_name] = command
                return command

            def subcommand(self, name: str):
                def outer(f: Callable[[types.ChatInteraction],  types.InteractionResponse]):
                    subcommand = SubCommand(name, f)
                    self.context[name] = subcommand
                    return subcommand
                return outer

            @contextmanager
            def group(self, name):
                group_context = {}
                old_context = self.context
                old_context[name] = group_context
                self.context = group_context
                yield self
                self.context = old_context

            # :grimacing:
            @property
            def description(self):
                return self.context["__description"]

            @description.setter
            def description(self, value: str):
                self.context["__description"] = value

            @description.deleter
            def description(self):
                del self.context["__description"]

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is None and exc_val is None and exc_tb is None:
                    children = {}
                    for (name, child) in self.context.items():
                        if name.startswith('__'):
                            continue

                        if isinstance(child, dict):
                            group = CommandGroup(name=name, description=child.get("__description", ""))
                            for (subname, subcommand) in child.items():
                                if subname.startswith('__'):
                                    continue
                                if not isinstance(subcommand, SubCommand):
                                    raise ValueError("Groups may not contain anything other than subcommands")
                                group.subcommands[subname] = subcommand
                            children[name]=group
                        else:
                            children[name] = child

                    meta_command = ChatMetaCommand(
                        name=outer_name,
                        children=children,
                        description=self.context.get("__description", "")
                    )
                    if outer_guild:
                        guild_commands[outer_guild][outer_name] = meta_command
                    else:
                        global_commands[outer_name] = meta_command
        return Builder()

    def init_app(self, app: Flask) -> None:
        self.public_key = app.config.setdefault("DISCORD_PUBLIC_KEY", "")
        if not self.public_key:
            raise ValueError("You must define a DISCORD_PUBLIC_KEY configuration value")

        interactions_bp = Blueprint('interactions', __name__, url_prefix="/discord")

        @interactions_bp.post('/interactions')
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
                            interaction = jsons.load(payload, types.ChatInteraction)
                        case types.CommandType.USER:
                            interaction = jsons.load(payload, types.UserInteraction)
                        case types.CommandType.MESSAGE:
                            interaction = jsons.load(payload, types.MessageInteraction)
                        case _:
                            raise ValueError("WTF Discord?")

                    result = self.runtime_commands[interaction.data.id](interaction)
                    if result:
                        return jsonify(jsons.dump(result, use_enum_name=False))
                case _:
                    pass
        app.register_blueprint(interactions_bp)
        # TODO: There should be a mechanism to opt-out of automatically init_commands-ing
        self.init_commands(app)

    def get_token(self, http):
        r = http.request(
            'POST',
            OAUTH_ENDPOINT, 
            fields={
                'grant_type': 'client_credentials',
                'scope': 'applications.commands.update'
            },
            headers=urllib3.util.make_headers(basic_auth=f"{self.client_id}:{self.client_secret}"),
            encode_multipart=False,
        )
        # r.raise_for_status()
        return json.loads(r.data.decode('utf-8'))

    def init_commands(self, app: Flask):
        self.client_id = app.config.setdefault("DISCORD_CLIENT_ID", "")
        self.client_secret = app.config.setdefault("DISCORD_CLIENT_SECRET", "")

        if not (self.client_id and self.client_secret):
            raise ValueError("You must define DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET configuration values")

        if not self.guild_commands and not self.global_commands:
            logger.warning(
                "Running init_commands with no commands defined!\n"
                "If you would like flask-discord-interactions to automatically push commands to Discord you will need to run `init_commands` _after_ defining your commands",
                self
            )
            return

        http = urllib3.PoolManager()
        token = self.get_token(http)
        http.headers = { 
            "Authorization": f"{token['token_type']} {token['access_token']}",
            "Content-Type": "application/json"
        }
        # TODO: Do I need to worry about token["expires_in"]?
        #       We don't actually ever re-use the token after init-ing the commands, so maybe not

        # TODO: Better (any) logs when things go wrong

        for (guild_id, commands) in self.guild_commands.items():
            for (_, command) in commands.items():
                url = GUILD_URL_TEMPLATE % (self.client_id, guild_id)
                resp = http.request("POST", url, body=json.dumps(command.spec()).encode('utf-8'))
                interaction_payload = json.loads(resp.data.decode('utf-8'))
                interaction = jsons.load(interaction_payload, types.ApplicationCommand)
                self.runtime_commands[interaction.id] = command

        for (_, command) in self.global_commands.items():
            url = GLOBAL_URL_TEMPLATE % self.client_id
            resp = http.request("POST", url, body=json.dumps(command.spec()).encode('utf-8'))
            interaction_payload = json.loads(resp.data.decode('utf-8'))
            interaction = jsons.load(interaction_payload, types.ApplicationCommand)
            self.runtime_commands[interaction.id] = command

# TODO: Design Components
