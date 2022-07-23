from contextlib import redirect_stdout
import io
from typing import cast

from discord_interactions_flask import Discord, ChatInteraction
from discord_interactions_flask import discord_types as types
from discord_interactions_flask import helpers


discord = Discord()
globals = {}
locals = {}


@discord.command("exec")
def bad_idea(interaction: ChatInteraction) -> types.InteractionResponse:
    assert interaction.data is not None
    assert interaction.data.options is not None
    code = cast(str, interaction.data.options[0].value)
    with redirect_stdout(io.StringIO()) as f:
        exec(code, globals, locals)
    output = f.getvalue() or "No Output"
    return helpers.content_response(output)


bad_idea.description = "Run Python code"

arg = types.ApplicationCommandOption(
    type=types.ApplicationCommandOptionType.STRING,
    name="code",
    description="The code to run",
    required=True,
)
bad_idea.add_option(arg)
