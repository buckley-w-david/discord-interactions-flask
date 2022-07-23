"""Builds :class:`Command` instances from functions."""
from collections.abc import Generator
from contextlib import contextmanager
import inspect
import logging
from typing import Callable, Optional, Union, cast, TYPE_CHECKING


from discord_interactions_flask import discord_types as types
from discord_interactions_flask.command import (
    ChatCommand,
    ChatMetaCommand,
    CommandGroup,
    MessageCommand,
    SubCommand,
    UserCommand,
)
from discord_interactions_flask import interactions

if TYPE_CHECKING:
    from discord_interactions_flask.discord import Discord


logger = logging.getLogger(__name__)

COMMANDS = {
    interactions.ChatInteraction: ChatCommand,
    interactions.UserInteraction: UserCommand,
    interactions.MessageInteraction: MessageCommand,
}

ChatFunction = Callable[[interactions.ChatInteraction], types.InteractionResponse]
UserFunction = Callable[[interactions.UserInteraction], types.InteractionResponse]
MessageFunction = Callable[[interactions.MessageInteraction], types.InteractionResponse]
# There is a term for why I need to specify the type like this instead of `Callable[[types.Interaction], types.InteractionResponse]` being able to apply to all three, I just forget what it is
# The rationale is that `Callable[[types.Interaction], types.InteractionResponse]` means "Function that can take any Interaction and returns an InteractionResponse"
# A function that can only take UserInteractions does not satisfy that
CommandFunction = Union[ChatFunction, UserFunction, MessageFunction]


# TODO: Add description param
class CommandBuilder:
    """Builds :class:`Command` instances from functions. Typically constructed with :meth:`~discord_interactions_flask.discord.Discord.command`."""

    def __init__(
        self,
        discord: 'Discord',
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

    def __call__(self, f: CommandFunction):
        """Decorate a command function to create a :class:`Command`.

        .. code-block:: python

            @discord.command()
            def command(interaction: interactions.ChatInteraction) -> types.InteractionResponse:
                return ...

        Args
            f: A callable that takes a :class:`interactions.ChatInteraction`, :class:`interactions.UserInteraction`, or :class:`interactions.MessageInteraction` instance and returns a :class:`types.InteractionResponse`.
        """
        signature = inspect.signature(f)
        param = list(signature.parameters.values())[0]
        if not (command_class := COMMANDS.get(param.annotation)):
            raise ValueError("Command parameter must be a valid Interaction type")

        if self.name:
            name = self.name
        else:
            name = f.__name__
        command = command_class(name, f)
        command.description = self._description
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
