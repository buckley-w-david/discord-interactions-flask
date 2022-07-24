from contextlib import redirect_stdout
import io
from typing import Optional

from flask import g

from discord_interactions_flask import Discord
from discord_interactions_flask import discord_types as types
from discord_interactions_flask import helpers


discord = Discord()


@discord.command("create", "Create a new command")
def create(
    name: str, code: str, description: Optional[str] = "No Description"
) -> types.InteractionResponse:
    guild = g.discord_interactions.ctx.data.guild_id

    @discord.command(name, description, guild)
    def new_command() -> types.InteractionResponse:
        with redirect_stdout(io.StringIO()) as f:
            exec(code, globals(), locals())
        output = f.getvalue() or "No Output"
        return helpers.content_response(output)

    return helpers.content_response(
        f"Created /{name}! I hope you know what you're doing!"
    )
