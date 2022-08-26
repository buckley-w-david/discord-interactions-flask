from dataclasses import dataclass, field
from functools import wraps
import typing
from typing import Union, Dict, Optional, Literal, Callable

from discord_interactions_flask.discord_types import (
    CommandType,
    ApplicationCommandOption,
)
from discord_interactions_flask import discord_types as types
from discord_interactions_flask import interactions
from discord_interactions_flask.jsons import BaseModel

ChatFunction = Callable[[interactions.ChatInteraction], types.InteractionResponse]
UserFunction = Callable[[interactions.UserInteraction], types.InteractionResponse]
MessageFunction = Callable[[interactions.MessageInteraction], types.InteractionResponse]

# This isn't great, but it's the best I've been able to figure out
# I want to somehow express that a ChatWithArgsFunction is a Callable with any number of args, all of which are a str, int, float, or bool
# I haven't been able to figure that out, the best I can do here is say that it's a function that takes some args, the first of which is one of those types
# The only "technically" correct way I can think of is generating all possible parameter combinations.
# There is a max of 25 params, and 8 possible types (4 normal + 4 optional variants)
# This results in 43_175_922_129_093_899_096_648 valid function signatures, all of which I would need to explicitly define
P = typing.ParamSpec("P")
ChatWithStrArgsFunction = Callable[
    typing.Concatenate[str, P], types.InteractionResponse
]
ChatWithOStrArgsFunction = Callable[
    typing.Concatenate[Optional[str], P], types.InteractionResponse
]
ChatWithIntArgsFunction = Callable[
    typing.Concatenate[int, P], types.InteractionResponse
]
ChatWithOIntArgsFunction = Callable[
    typing.Concatenate[Optional[int], P], types.InteractionResponse
]
ChatWithFloatArgsFunction = Callable[
    typing.Concatenate[float, P], types.InteractionResponse
]
ChatWithOFloatArgsFunction = Callable[
    typing.Concatenate[Optional[float], P], types.InteractionResponse
]
ChatWithBoolArgsFunction = Callable[
    typing.Concatenate[bool, P], types.InteractionResponse
]
ChatWithOBoolArgsFunction = Callable[
    typing.Concatenate[Optional[bool], P], types.InteractionResponse
]
ChatWithNoArgsFunction = Callable[[], types.InteractionResponse]
ChatWithArgsFunction = Union[
    ChatWithStrArgsFunction,
    ChatWithIntArgsFunction,
    ChatWithFloatArgsFunction,
    ChatWithBoolArgsFunction,
    ChatWithOStrArgsFunction,
    ChatWithOIntArgsFunction,
    ChatWithOFloatArgsFunction,
    ChatWithOBoolArgsFunction,
    ChatWithNoArgsFunction,
]

CommandFunction = Union[
    ChatFunction, UserFunction, MessageFunction, ChatWithArgsFunction
]


class Command(BaseModel):
    def spec(self) -> dict:
        return self.dump(
            use_enum_name=False, strip_privates=True, strip_properties=True
        )


@dataclass
class ChatCommand(Command):
    name: str  # Name of command, 1-32 characters
    description: str  # 1-100 character description
    type: Optional[
        Literal[CommandType.CHAT]
    ] = (
        CommandType.CHAT
    )  # one of application command type # Type of command, defaults 1 if not set
    name_localizations: Optional[
        dict[str, str]
    ] = None  # Localization dictionary for the name field. Values follow the same restrictions as name
    description_localizations: Optional[
        dict[str, str]
    ] = None  # Localization dictionary for the description field. Values follow the same restrictions as description
    options: Optional[
        list[ApplicationCommandOption]
    ] = None  # the parameters for the command
    default_member_permissions: Optional[
        str
    ] = None  # Set of permissions represented as a bit set
    dm_permission: Optional[
        bool
    ] = None  # Indicates whether the command is available in DMs with the app, only for globally-scoped commands. By default, commands are visible.

    def add_option(self, option: types.ApplicationCommandOption):
        if not self.options:
            self.options = [option]
        else:
            self.options.append(option)

    def handler(self, f: ChatFunction):
        wraps(f)(self)
        self._func = f
        return self

    @property
    def interaction_handler(self) -> Optional[ChatFunction]:
        return self._func

    @interaction_handler.setter
    def interaction_handler(self, f: ChatFunction):
        self.handler(f)

    def __call__(self, interaction: interactions.ChatInteraction):
        return self._func(interaction)


@dataclass
class UserCommand(Command):
    name: str  # Name of command, 1-32 characters
    type: Literal[
        CommandType.USER
    ] = (
        CommandType.USER
    )  # one of application command type # Type of command, defaults 1 if not set
    name_localizations: Optional[
        dict[str, str]
    ] = None  # Localization dictionary for the name field. Values follow the same restrictions as name
    default_member_permissions: Optional[
        str
    ] = None  # Set of permissions represented as a bit set
    dm_permission: Optional[
        bool
    ] = None  # Indicates whether the command is available in DMs with the app, only for globally-scoped commands. By default, commands are visible.

    def handler(self, f: UserFunction):
        wraps(f)(self)
        self._func = f
        return self

    @property
    def interaction_handler(self) -> Optional[UserFunction]:
        return self._func

    @interaction_handler.setter
    def interaction_handler(self, f: UserFunction):
        self.handler(f)

    def __call__(self, interaction: interactions.UserInteraction):
        return self._func(interaction)


@dataclass
class MessageCommand(Command):
    name: str  # Name of command, 1-32 characters
    type: Literal[
        CommandType.MESSAGE
    ] = (
        CommandType.MESSAGE
    )  # one of application command type # Type of command, defaults 1 if not set
    name_localizations: Optional[
        dict[str, str]
    ] = None  # Localization dictionary for the name field. Values follow the same restrictions as name
    default_member_permissions: Optional[
        str
    ] = None  # Set of permissions represented as a bit set
    dm_permission: Optional[
        bool
    ] = None  # Indicates whether the command is available in DMs with the app, only for globally-scoped commands. By default, commands are visible.

    def handler(self, f: MessageFunction):
        wraps(f)(self)
        self._func = f
        return self

    @property
    def interaction_handler(self) -> Optional[MessageFunction]:
        return self._func

    @interaction_handler.setter
    def interaction_handler(self, f: MessageFunction):
        self.handler(f)

    def __call__(self, interaction: interactions.MessageInteraction):
        return self._func(interaction)


@dataclass
class ChatCommandWithArgs(ChatCommand):
    def handler(self, f: ChatWithArgsFunction):
        wraps(f)(self)
        self._func = f
        return self

    @property
    def interaction_handler(self) -> Optional[ChatWithArgsFunction]:
        return self._func

    @interaction_handler.setter
    def interaction_handler(self, f: ChatWithArgsFunction):
        self.handler(f)

    def __call__(self, interaction: interactions.ChatInteraction):
        if interaction.data.options:
            kwargs = {option.name: option.value for option in interaction.data.options}
        else:
            kwargs = {}

        # FIXME: Might have to rethink the ChatWithArgsFunction definition, pyright doesn't like it here
        return self._func(**kwargs)  # type: ignore


@dataclass
class SubCommand(ChatCommand):
    type: Literal[
        types.ApplicationCommandOptionType.SUB_COMMAND
    ] = (
        types.ApplicationCommandOptionType.SUB_COMMAND
    )  # one of application command type # Type of command, defaults 1 if not set


@dataclass
class CommandGroup(BaseModel):
    name: str
    description: str
    type: Literal[
        types.ApplicationCommandOptionType.SUB_COMMAND_GROUP
    ] = types.ApplicationCommandOptionType.SUB_COMMAND_GROUP
    _subcommands: Dict[str, SubCommand] = field(default_factory=dict)

    def spec(self) -> dict:
        spec: dict = self.dump(
            use_enum_name=False, strip_privates=True, strip_properties=True
        )
        spec["options"] = [v.spec() for _, v in self._subcommands.items()]
        return spec

    @property
    def options(self):
        return [v for _, v in self._subcommands.items()]

    def add_child(self, subcommand: SubCommand):
        self._subcommands[subcommand.name] = subcommand

    def __call__(
        self, interaction: interactions.ChatInteraction
    ) -> types.InteractionResponse:
        if not interaction.data.options:
            raise ValueError("This should be impossible")

        group_options = interaction.data.options[0]
        if not group_options.options:
            raise ValueError(
                "Expected group to have options to define subcommand options"
            )

        subcommand_data = group_options.options[0]
        subcommand = self._subcommands[subcommand_data.name]
        return subcommand(interaction)


@dataclass
class ChatMetaCommand(ChatCommand):
    _children: Dict[str, Union[CommandGroup, SubCommand]] = field(default_factory=dict)

    def spec(self) -> dict:
        spec: dict = self.dump(
            use_enum_name=False, strip_privates=True, strip_properties=True
        )
        spec["options"] = [v.spec() for _, v in self._children.items()]
        return spec

    def add_child(self, child: Union[CommandGroup, SubCommand]):
        self._children[child.name] = child

    @property
    def options(self):
        return [v for _, v in self._children.items()]

    @options.setter
    def options(self, _):
        pass

    def __call__(
        self, interaction: interactions.ChatInteraction
    ) -> types.InteractionResponse:
        if not interaction.data.options:
            raise ValueError("Expected meta command to have a group or subcommand")

        data = interaction.data.options[0]
        command = self._children[data.name]
        if not command:
            raise ValueError("Subcomand is not part of this ChatMetaCommand")

        return command(interaction)


BaseCommand = Union[ChatCommand, UserCommand, MessageCommand]
