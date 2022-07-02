from dataclasses import dataclass, field
from functools import wraps
from typing import List, Union, Dict
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
    description: str =  ""
    subcommands: Dict[str, SubCommand] = field(default_factory=dict)

    def spec(self):
        return {
            "name": self.name,
            "description": self.description,
            "type": types.ApplicationCommandOptionType.SUB_COMMAND_GROUP,
            "options": [sc.spec() for (_, sc) in self.subcommands.items()]
        }

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
            "options": [child.spec() for (_, child) in self.children.items()]
        }

    # TODO: Dispatch to correct subcommand
    def __call__(self, *args, **kwargs):
        pass

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
