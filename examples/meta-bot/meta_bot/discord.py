from contextlib import redirect_stdout
import io
from typing import cast

from discord_interactions_flask import Discord, ChatInteraction
from discord_interactions_flask import discord_types as types
from discord_interactions_flask import helpers


discord = Discord()


@discord.command("create")
def create(interaction: ChatInteraction) -> types.InteractionResponse:
    assert interaction.data is not None
    assert interaction.data.options is not None
    name = cast(str, interaction.data.options[0].value)
    code = cast(str, interaction.data.options[1].value)

    if len(interaction.data.options) == 3:
        description = cast(str, interaction.data.options[2].value)
    else:
        description = "No Description"

    @discord.command(name, description, interaction.data.guild_id)
    def new_command(interaction: ChatInteraction) -> types.InteractionResponse:
        with redirect_stdout(io.StringIO()) as f:
            exec(code, globals(), locals())
        output = f.getvalue() or "No Output"
        return helpers.content_response(output)

    return helpers.content_response(
        f"Created /{name}! I hope you know what you're doing!"
    )


create.description = "Create a new command"

name = types.ApplicationCommandOption(
    type=types.ApplicationCommandOptionType.STRING,
    name="name",
    description="the name of the command",
    required=True,
)
code = types.ApplicationCommandOption(
    type=types.ApplicationCommandOptionType.STRING,
    name="code",
    description="The code to run",
    required=True,
)
description = types.ApplicationCommandOption(
    type=types.ApplicationCommandOptionType.STRING,
    name="description",
    description="the description of the command",
    required=False,
)
create.add_option(name)
create.add_option(code)
create.add_option(description)
