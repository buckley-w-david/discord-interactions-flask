import os
from typing import Optional

from discord_interactions_flask import Discord
from discord_interactions_flask import discord_types as types
from discord_interactions_flask import interactions
from discord_interactions_flask import components
from discord_interactions_flask.helpers import content_response
from flask import Flask

discord = Discord()


def button_response_2(
    interaction: interactions.ButtonInteraction,
) -> types.InteractionResponse:
    return content_response("Hello, World 2!")


@discord.command("slash-example", "Say Hello via a slash command")
def chat_command() -> types.InteractionResponse:
    button = components.Button(
        custom_id="button-1",
        label="Push me!",
        style=types.ButtonStyle.PRIMARY,
    )

    @button.handler
    def button_response(
        interaction: interactions.ButtonInteraction,
    ) -> types.InteractionResponse:
        return content_response("Hello, World!")

    button_2 = components.Button(
        custom_id="button-2",
        label="Push me as well!",
        style=types.ButtonStyle.SECONDARY,
    )
    button_2.interaction_handler = button_response_2

    select_menu = components.SelectMenu(
        custom_id="input-1",
        options=[
            types.SelectOption(
                label="label-1",
                value="value-1",
            )
        ],
    )

    @select_menu.handler
    def sm_response(
        interaction: interactions.SelectMenuInteraction,
    ) -> types.InteractionResponse:
        return content_response(f"You selected: {interaction.data.values[0]}")

    return types.InteractionResponse(
        type=types.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
        data=types.InteractionCallbackDataMessage(
            content="Slash!",
            components=[
                types.ActionRow(components=[button, button_2]),
                types.ActionRow(components=[select_menu]),
            ],
        ),
    )


@discord.command("User Example")
def user_command(
    interaction: interactions.UserInteraction,
) -> types.InteractionResponse:
    return content_response("Hello, World!")


@discord.command("Message Example")
def message_command(
    interaction: interactions.MessageInteraction,
) -> types.InteractionResponse:
    if resolved := interaction.data.resolved:
        messages = resolved.messages
        _, message = messages.popitem()  # type: ignore
        content = message.content
    else:
        content = "fallback"

    return content_response(content)


with discord.command("slash-group", "Example command with groups") as command:

    @command.subcommand("sub-1")
    def sub_1(interaction: interactions.ChatInteraction) -> types.InteractionResponse:
        return content_response("Hello from sub-1!")

    @command.subcommand("sub-2")
    def sub_2(interaction: interactions.ChatInteraction) -> types.InteractionResponse:
        return content_response("Hello from sub-2!")

    with command.group("group-1", "Group description") as group:

        @group.subcommand("sub-3")
        def sub_3(
            interaction: interactions.ChatInteraction,
        ) -> types.InteractionResponse:
            return content_response("Hello from sub-3!")

        @group.subcommand("sub-4")
        def sub_4(
            interaction: interactions.ChatInteraction,
        ) -> types.InteractionResponse:
            return content_response("Hello from sub-4!")


@discord.command()
def echo(text: str, times: Optional[int] = None) -> types.InteractionResponse:
    lines = [text for _ in range(times or 1)]
    return content_response("\n".join(lines))


app = Flask(__name__)
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

discord.init_app(app)
