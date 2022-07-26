"""Builds :class:`Command` instances from functions."""
from collections.abc import Generator
from contextlib import contextmanager
import inspect
import typing
from typing import Callable, Optional, TYPE_CHECKING


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
    ChatFunction,
    UserFunction,
    MessageFunction,
    ChatWithArgsFunction,
    CommandFunction,
)
from discord_interactions_flask import interactions

if TYPE_CHECKING:
    from discord_interactions_flask.discord import Discord


def _make_chat_command(name: str, description: str, func: ChatFunction) -> ChatCommand:
    command = ChatCommand(name=name, description=description)
    command.interaction_handler = func
    return command


def _make_user_command(name: str, _: str, func: UserFunction) -> UserCommand:
    command = UserCommand(name=name)
    command.interaction_handler = func
    return command


def _make_message_command(name: str, _: str, func: MessageFunction) -> MessageCommand:
    command = MessageCommand(name=name)
    command.interaction_handler = func
    return command


COMMANDS = {
    interactions.ChatInteraction: _make_chat_command,
    interactions.UserInteraction: _make_user_command,
    interactions.MessageInteraction: _make_message_command,
}


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
        name: Optional[str] = None,
        description: Optional[str] = None,
        guild_id: Optional[str] = None,
    ):
        """Initialize :class:`CommandBuilder`.

        Args
            discord: A reference to a :class:`discord_interactions_flask.discord.Discord`.

            name: An optional name to give the command. If not given the function name will be used.

            description: An optional description to give the command. If not given the name will be used.

            guild_id: An optional guild_id. If given the command will be created in just that guild.
        """
        self.discord = discord
        self.name = name
        self.description = description
        self.guild_id = guild_id

    # NOTE: These overloads expose a bug in the type checker
    #       When all the interaction types share a parent class
    #       it finds each *Function definition an equallty good match
    #       for any of the overloads, so always picks the first one
    #       This seems to be caused by all of the *Interaction types
    #       sharing a common parent class.
    #       I _could_ attempt to snip that common parent by duplicating a bunch
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
        command = self._create(f)
        self.discord.add_command(command, self.guild_id)
        return command

    def _create(self, f: CommandFunction) -> BaseCommand:
        # TODO: I should make this usable for subcommands
        #       Right now a subset of the logic is duplicated, and they don't get access
        #       to the nice ChatCommandWithArgs feature
        if self.name:
            name = self.name
        else:
            name = f.__name__

        description = self.description or name

        signature = inspect.signature(f)
        if signature.parameters and (
            command_class := COMMANDS.get(
                list(signature.parameters.values())[0].annotation
            )
        ):
            command = command_class(name, description, f)
        else:
            command = ChatCommandWithArgs(name, description)
            command.interaction_handler = f  # type: ignore
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

        return command

    def subcommand(
        self, name: Optional[str] = None, description: Optional[str] = None
    ) -> Callable[[ChatFunction], SubCommand]:
        """Create a decorator for a command function to create a :class:`Command`. Should only be used within a :func:`group`.

        .. code-block:: python

            @group.subcommand("sub-command")
            def sub_command(interaction: interactions.ChatInteraction) -> types.InteractionResponse:
                return ...

        Args
            name: An optional name to give the subcommand. If not given the functions name is used.

            description: An optional description to give the subcommand. If not given name is used.
        """

        def outer(f: ChatFunction) -> SubCommand:
            if not name:
                command_name = f.__name__
            else:
                command_name = name

            command_description = description or command_name

            subcommand = SubCommand(name=command_name, description=command_description)
            subcommand.interaction_handler = f
            self.context.add_child(subcommand)
            return subcommand

        return outer

    @contextmanager
    def group(
        self, name: str, description: Optional[str] = None
    ) -> Generator["CommandBuilder", None, None]:
        """Create a subcommand group.

        .. code-block:: python

            with command.group("group_name", "group description) as group:
                @group.subcommand()
                ...

        Args
            name: An name for the group.

            description: An name for the group.
        """
        old_context = self.context
        description = description or name
        group = CommandGroup(name=name, description=description)
        old_context.add_child(group)
        self.context = group
        yield self
        self.context = old_context

    def __enter__(self) -> "CommandBuilder":
        """Create subcommands and commad grounp.

        .. code-block:: python

            with discord.command("command-name") as command:
                with command.group("group") as group:
                    @group.subcommand()
                    ...
                @command.subcommand()
                def subcommand(...):
                    ...
        """
        if not self.name:
            raise ValueError("Commands created with the context manager require a name")

        description = self.description or self.name

        self.context = ChatMetaCommand(name=self.name, description=description)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Build the Command containing the groups/subcommands defined with this Builder."""
        if exc_type is None and exc_val is None and exc_tb is None:
            assert isinstance(self.context, ChatMetaCommand)
            self.discord.add_command(self.context, self.guild_id)
