import os
from dataclasses import asdict

from flask_discord_interactions import Discord
from flask_discord_interactions import discord_types as types
from flask import Flask

discord = Discord()

@discord.command("slash-example")
def chat_command(interaction: types.ChatInteraction) -> types.InteractionResponse:
    return types.InteractionResponse(
        type=types.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
        data=types.InteractionCallbackDataMessages(
            content="Hello, World!"
        )
    )
chat_command.description = "Say Hello via a slash command"

@discord.command("User Example")
def user_command(interaction: types.UserInteraction) -> types.InteractionResponse:
    return types.InteractionResponse(
        type=types.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
        data=types.InteractionCallbackDataMessages(
            content="Hello, <@%s>!" % interaction.data.target_id
        )
    )

@discord.command("Message Example")
def message_command(interaction: types.MessageInteraction) -> types.InteractionResponse:
    if (resolved := interaction.data.resolved):
        messages = resolved.messages
        _, message = messages.popitem() # type: ignore
        content = message["content"]
    else:
        content = "fallback"

    return types.InteractionResponse(
        type=types.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
        data=types.InteractionCallbackDataMessages(
            tts=True,
            content=content,
        )
    )

with discord.command("slash-group") as command:
    command.description = "Example command with grous"
    @command.subcommand("sub-1")
    def sub_1(interaction: types.ChatInteraction) -> types.InteractionResponse:
        return types.InteractionResponse(
            type=types.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
            data=types.InteractionCallbackDataMessages(
                content="Hello from sub-1!"
            )
        )
    sub_1.description = "sub-1"

    @command.subcommand("sub-2")
    def sub_2(interaction: types.ChatInteraction) -> types.InteractionResponse:
        return types.InteractionResponse(
            type=types.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
            data=types.InteractionCallbackDataMessages(
                content="Hello from sub-2!"
            )
        )
    sub_2.description = "sub-2"

    with command.group("group-1") as group:
        group.description = "Group description"
        @group.subcommand("sub-3")
        def sub_3(interaction: types.ChatInteraction) -> types.InteractionResponse:
            return types.InteractionResponse(
                type=types.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                data=types.InteractionCallbackDataMessages(
                    content="Hello from sub-3!"
                )
            )
        sub_3.description = "sub-3"

        @group.subcommand("sub-4")
        def sub_4(interaction: types.ChatInteraction) -> types.InteractionResponse:
            return types.InteractionResponse(
                type=types.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                data=types.InteractionCallbackDataMessages(
                    content="Hello from sub-4!"
                )
            )
        sub_4.description = "sub-4"

app = Flask(__name__)
app.config['DISCORD_PUBLIC_KEY'] = os.environ['DISCORD_PUBLIC_KEY']
app.config['DISCORD_CLIENT_ID'] = os.environ['DISCORD_CLIENT_ID']
app.config['DISCORD_CLIENT_SECRET'] = os.environ['DISCORD_CLIENT_SECRET']

discord.init_app(app)
