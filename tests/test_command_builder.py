import typing

from discord_interactions_flask import Discord
from discord_interactions_flask.command_builder import CommandBuilder
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
from discord_interactions_flask.discord_types import InteractionResponse


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


def test_builder_subcommand():
    d = Discord()
    builder = d.command("meta")

    with builder as command:
        command.description = "top level description"
        subcommand = command.subcommand("subname")(chat_function)
        subcommand.description = "test"

    meta_command = d.commands[None]["meta"]
    assert isinstance(meta_command, ChatMetaCommand)
    assert meta_command.name == "meta"
    assert meta_command.description == "top level description"
    assert subcommand is meta_command.children["subname"]


def test_builder_group():
    d = Discord()
    builder = d.command("meta")

    with builder as command:
        command.description = "top level description"
        with command.group("group") as group:
            group.description = "group level description"
            subcommand = command.subcommand("subname")(chat_function)
            subcommand.description = "test"

    _, meta_command = d.commands[None].popitem()
    meta_command = typing.cast(ChatMetaCommand, meta_command)
    
    group = typing.cast(CommandGroup, meta_command.children["group"])
    assert meta_command.description == "top level description"
    assert group.name == "group"
    assert group.description == "group level description"
    assert group.subcommands["subname"] is subcommand
