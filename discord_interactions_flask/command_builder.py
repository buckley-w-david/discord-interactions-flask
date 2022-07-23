"""Builds :class:`Command` instances from functions."""
from collections.abc import Generator
from contextlib import contextmanager
import inspect
import typing
from typing import Callable, Optional, Union, TYPE_CHECKING


from discord_interactions_flask import discord_types as types
from discord_interactions_flask.command import (
    ChatCommand,
    ChatCommandWithArgs,
    ChatMetaCommand,
    CommandGroup,
    MessageCommand,
    SubCommand,
    UserCommand,
    BaseCommand,
)
from discord_interactions_flask import interactions

if TYPE_CHECKING:
    from discord_interactions_flask.discord import Discord


COMMANDS = {
    interactions.ChatInteraction: ChatCommand,
    interactions.UserInteraction: UserCommand,
    interactions.MessageInteraction: MessageCommand,
}

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
ChatWithArgsFunction = Union[
    ChatWithStrArgsFunction,
    ChatWithIntArgsFunction,
    ChatWithFloatArgsFunction,
    ChatWithBoolArgsFunction,
    ChatWithOStrArgsFunction,
    ChatWithOIntArgsFunction,
    ChatWithOFloatArgsFunction,
    ChatWithOBoolArgsFunction,
]

CommandFunction = Union[
    ChatFunction, UserFunction, MessageFunction, ChatWithArgsFunction
]

TYPE_OPTION_MAP = {
    str: types.ApplicationCommandOptionType.STRING,
    int: types.ApplicationCommandOptionType.INTEGER,
    bool: types.ApplicationCommandOptionType.BOOLEAN,
    float: types.ApplicationCommandOptionType.NUMBER,
}

# Where is this supposed to come from?
NoneType = type(None)


class CommandBuilder:
    """Builds :class:`Command` instances from functions. Typically constructed with :meth:`~discord_interactions_flask.discord.Discord.command`."""

    def __init__(
        self,
        discord: "Discord",
        name: Optional[str],
        description: Optional[str],
        guild_id: Optional[str],
    ):
        """Initialize :class:`CommandBuilder`.

        Args
            discord: A reference to a :class:`discord_interactions_flask.discord.Discord`.
            name: An optional name to use for the command. If not present the command functions name will be used.
        """
        self.discord = discord
        self.name = name
        self.guild_id = guild_id
        self._description = description

        self.context = {}

    # NOTE: These overloads expose a bug in the type checker
    #       When all the interaction types share a parent class
    #       it finds each *Function definition an equallty good match
    #       for any of the overloads, so always picks the first one
    #       I _could_ attempt to snip that common ancestor by duplicating a bunch
    #       of defintions, but after trying it it seems more trouble than it's worth
    @typing.overload
    def __call__(self, f: ChatFunction) -> ChatCommand:
        ...

    @typing.overload
    def __call__(self, f: UserFunction) -> UserCommand:
        ...

    @typing.overload
    def __call__(self, f: MessageFunction) -> MessageCommand:
        ...

    @typing.overload
    def __call__(self, f: ChatWithArgsFunction) -> ChatCommand:
        ...

    def __call__(self, f: CommandFunction) -> BaseCommand:
        """Decorate a command function to create a :class:`Command`.

        .. code-block:: python

            @discord.command()
            def command(interaction: interactions.ChatInteraction) -> types.InteractionResponse:
                return ...

        Args
            f: A callable that takes a :class:`interactions.ChatInteraction`, :class:`interactions.UserInteraction`, or :class:`interactions.MessageInteraction` instance and returns a :class:`types.InteractionResponse`.
        """
        if self.name:
            name = self.name
        else:
            name = f.__name__
        signature = inspect.signature(f)
        param = list(signature.parameters.values())[0]
        if command_class := COMMANDS.get(param.annotation):
            command = command_class(name, f)
            command.description = self._description
        else:
            command = ChatCommandWithArgs(name, f)
            command.description = self._description or ""
            for param in signature.parameters.values():
                annotation = param.annotation
                required = True

                if typing.get_origin(annotation) is typing.Union:
                    sub_types = typing.get_args(annotation)
                    if len(sub_types) != 2 or sub_types[1] is not NoneType:
                        raise ValueError("Only Optional type unions are supported")
                    required = False
                    annotation = sub_types[0]

                type_ = TYPE_OPTION_MAP.get(annotation)  # type: ignore
                if type_ is None:
                    raise ValueError(f"{annotation} is not a supported argument type")

                command.add_option(
                    types.ApplicationCommandOption(
                        type=type_,
                        name=param.name,
                        description=param.name,
                        required=required,
                    )
                )

        self.discord.add_command(name, command, self.guild_id)
        return command

    def subcommand(
        self, name: Optional[str] = None
    ) -> Callable[[ChatFunction], SubCommand]:
        """Create a decorator for a command function to create a :class:`Command`. Should only be used within a :func:`group`.

        .. code-block:: python

            @group.subcommand("sub-command")
            def sub_command(interaction: interactions.ChatInteraction) -> types.InteractionResponse:
                return ...

        Args
            name: An optional name to give the subcommand. If not given the functions name is used.
        """

        def outer(f: ChatFunction) -> SubCommand:
            if not name:
                command_name = f.__name__
            else:
                command_name = name

            subcommand = SubCommand(command_name, f)
            self.context[name] = subcommand
            return subcommand

        return outer

    @contextmanager
    def group(self, name: str) -> Generator["CommandBuilder", None, None]:
        """Create a subcommand group.

        .. code-block:: python

            with command.group("group_name") as group:
                group.description = ...
                @group.subcommand()
                ...

        Args
            name: An name for the group.
        """
        group_context = {}
        old_context = self.context
        old_context[name] = group_context
        self.context = group_context
        yield self
        self.context = old_context

    # :grimacing:
    # I don't like this hacky solution around command/group description
    @property
    def description(self):
        """Set the description used for the current command/group."""
        return self.context["__description"]

    @description.setter
    def description(self, value: str):
        self.context["__description"] = value

    @description.deleter
    def description(self):
        del self.context["__description"]

    def __enter__(self) -> "CommandBuilder":
        """Create subcommands and commad grounp.

        .. code-block:: python

            with discord.command("command-name") as command:
                command.description = ...
                with command.group("group") as group:
                    group.description = ...
                    @group.subcommand()
                    ...
                @command.subcommand()
                def subcommand(...):
                    ...
        """
        if not self.name:
            raise ValueError("Commands created with the context manager require a name")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Build the Command containing the groups/subcommands defined with this Builder."""
        if exc_type is None and exc_val is None and exc_tb is None:
            children = {}
            for (name, child) in self.context.items():
                if name.startswith("__"):
                    continue

                if isinstance(child, dict):
                    group = CommandGroup(
                        name=name, description=child.get("__description", "")
                    )
                    for (subname, subcommand) in child.items():
                        if subname.startswith("__"):
                            continue
                        if not isinstance(subcommand, SubCommand):
                            raise ValueError(
                                "Groups may not contain anything other than subcommands"
                            )
                        group.subcommands[subname] = subcommand
                    children[name] = group
                else:
                    children[name] = child

            assert self.name is not None
            meta_command = ChatMetaCommand(
                name=self.name,
                children=children,
                description=self.context.get("__description", ""),
            )
            self.discord.add_command(self.name, meta_command, self.guild_id)
