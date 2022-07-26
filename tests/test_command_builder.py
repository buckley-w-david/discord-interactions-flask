import typing
from typing import Optional

import pytest

from discord_interactions_flask import Discord
from discord_interactions_flask.interactions import (
    ChatInteraction,
    UserInteraction,
    MessageInteraction,
)
from discord_interactions_flask.command import (
    ChatCommand,
    UserCommand,
    MessageCommand,
    ChatMetaCommand,
    CommandGroup,
)
from discord_interactions_flask.discord_types import (
    InteractionResponse,
    ApplicationCommandOptionType,
)


def chat_function(i: ChatInteraction) -> InteractionResponse:
    return InteractionResponse()


def user_function(i: UserInteraction) -> InteractionResponse:
    return InteractionResponse()


def message_function(i: MessageInteraction) -> InteractionResponse:
    return InteractionResponse()


def test_builder_build_chat_command():
    d = Discord()
    builder = d.command()

    command = builder(chat_function)
    assert isinstance(command, ChatCommand)
    assert command.name == "chat_function"
    assert command in d.commands[None].values()


def test_builder_build_user_command():
    d = Discord()
    builder = d.command()

    command = builder(user_function)
    assert isinstance(command, UserCommand)
    assert command.name == "user_function"
    assert command in d.commands[None].values()


def test_builder_build_message_command():
    d = Discord()
    builder = d.command()

    command = builder(message_function)
    assert isinstance(command, MessageCommand)
    assert command.name == "message_function"
    assert command in d.commands[None].values()


def chat_with_args(
    s: str, i: int, f: float, os: Optional[str], oi: Optional[int], of: Optional[float]
) -> InteractionResponse:
    return InteractionResponse()


def test_builder_build_chat_with_args_command():
    d = Discord()
    builder = d.command()

    command = builder(chat_with_args)
    assert isinstance(command, ChatCommand)
    options = command.options
    assert options is not None

    assert len(options) == 6

    assert options[0].name == "s"
    assert options[0].type == ApplicationCommandOptionType.STRING
    assert options[0].required
    assert options[1].name == "i"
    assert options[1].type == ApplicationCommandOptionType.INTEGER
    assert options[1].required
    assert options[2].name == "f"
    assert options[2].type == ApplicationCommandOptionType.NUMBER
    assert options[2].required

    assert options[3].name == "os"
    assert options[3].type == ApplicationCommandOptionType.STRING
    assert not options[4].required
    assert options[4].name == "oi"
    assert options[4].type == ApplicationCommandOptionType.INTEGER
    assert not options[4].required
    assert options[5].name == "of"
    assert options[5].type == ApplicationCommandOptionType.NUMBER
    assert not options[5].required


def empty() -> InteractionResponse:
    return InteractionResponse()


def test_builder_build_empty_command():
    d = Discord()
    builder = d.command()

    command = builder(empty)
    assert isinstance(command, ChatCommand)
    assert not command.options


def invalid(a: dict) -> InteractionResponse:
    return InteractionResponse()


def test_builder_build_invalid_command_raises_value_error():
    d = Discord()
    builder = d.command()

    with pytest.raises(ValueError):
        command = builder(invalid)


def test_builder_subcommand():
    d = Discord()
    builder = d.command("meta", "top level description")

    with builder as command:
        subcommand = command.subcommand("subname")(chat_function)
        subcommand.description = "test"

    meta_command = d.commands[None]["meta"]
    assert isinstance(meta_command, ChatMetaCommand)
    assert meta_command.name == "meta"
    assert meta_command.description == "top level description"
    assert subcommand is meta_command._children["subname"]


def test_builder_group():
    d = Discord()
    builder = d.command("meta", "top level description")

    with builder as command:
        with command.group("group", "group level description") as group:
            subcommand = command.subcommand("subname")(chat_function)
            subcommand.description = "test"

    _, meta_command = d.commands[None].popitem()
    meta_command = typing.cast(ChatMetaCommand, meta_command)

    group = typing.cast(CommandGroup, meta_command._children["group"])
    assert meta_command.description == "top level description"
    assert group.name == "group"
    assert group.description == "group level description"
    assert group._subcommands["subname"] is subcommand
