from dataclasses import dataclass, field
from functools import wraps
from typing import Union, Dict, cast
import jsons

from flask_discord_interactions.discord_types import CommandType
from flask_discord_interactions import discord_types as types


class ChatCommand:
    def __init__(self, name: str, func):
        self.name = name
        self.func = func
        self.description = ""
        self.options = []
        wraps(func)(self)

    def add_option(self, option: types.ApplicationCommandOption):
        self.options.append(option)

    def spec(self) -> dict:
        return {
            "name": self.name,
            "type": CommandType.CHAT,
            "description": self.description,
            "options": [jsons.dump(o, use_enum_name=False) for o in self.options],
        }

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class SubCommand(ChatCommand):
    def spec(self) -> dict:
        spec = super().spec()
        spec["type"] = types.ApplicationCommandOptionType.SUB_COMMAND
        return spec


@dataclass
class CommandGroup:
    name: str
    description: str = ""
    subcommands: Dict[str, SubCommand] = field(default_factory=dict)

    def spec(self):
        return {
            "name": self.name,
            "description": self.description,
            "type": types.ApplicationCommandOptionType.SUB_COMMAND_GROUP,
            "options": [sc.spec() for (_, sc) in self.subcommands.items()],
        }

    def __call__(self, interaction: types.ChatInteraction, group_options: types.ApplicationCommandInteractionDataOption) -> types.InteractionResponse:
        if not group_options.options:
            raise ValueError("Expected group to have options to define subcommand options")

        subcommand_data = group_options.options[0]
        subcommand = self.subcommands[subcommand_data.name]
        return subcommand(interaction)


@dataclass
class ChatMetaCommand:
    name: str
    children: Dict[str, Union[CommandGroup, SubCommand]]
    description: str = ""

    def spec(self):
        return {
            "name": self.name,
            "type": CommandType.CHAT,
            "description": self.description,
            "options": [child.spec() for (_, child) in self.children.items()],
        }

    def __call__(self, interaction: types.ChatInteraction) -> types.InteractionResponse:
        if not interaction.data.options:
            raise ValueError("Expected meta command to have a group or subcommand")

        data = interaction.data.options[0]
        match data.type:
            case types.ApplicationCommandOptionType.SUB_COMMAND_GROUP:
                group = cast(CommandGroup, self.children[data.name])
                return group(interaction, data)
            case types.ApplicationCommandOptionType.SUB_COMMAND:
                subcommand = cast(SubCommand, self.children[data.name])
                return subcommand(interaction)
            case _:
                raise ValueError("Invalid interaction type in options")


class UserCommand:
    def __init__(self, name: str, func):
        self.name = name
        self.func = func
        wraps(func)(self)

    def spec(self) -> dict:
        return {
            "name": self.name,
            "type": CommandType.USER,
        }

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class MessageCommand:
    def __init__(self, name: str, func):
        self.name = name
        self.func = func
        wraps(func)(self)

    def spec(self) -> dict:
        return {
            "name": self.name,
            "type": CommandType.MESSAGE,
        }

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


Command = Union[ChatCommand, ChatMetaCommand, UserCommand, MessageCommand]
