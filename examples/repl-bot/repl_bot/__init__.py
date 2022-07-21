import os
from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
    app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
    app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

    from repl_bot.discord import discord

    discord.init_app(app)

    return app
