# flask-discord-interactions

A [Flask](https://github.com/pallets/flask/) extension to support interacting with [Discord Interactions](https://discord.com/developers/docs/interactions/application-commands).

Check out the [quickstart](https://docs.davidbuckley.ca/flask-discord-interactions/usage/quickstart.html) or the [examples directory](/examples) for an idea of how to use it.

```python
import os

from flask import Flask

from flask_discord_interactions import Discord
from flask_discord_interactions import discord_types as types

app = Flask(__name__)
app.config['DISCORD_PUBLIC_KEY'] = os.environ['DISCORD_PUBLIC_KEY']
app.config['DISCORD_CLIENT_ID'] = os.environ['DISCORD_CLIENT_ID']
app.config['DISCORD_CLIENT_SECRET'] = os.environ['DISCORD_CLIENT_SECRET']

discord = Discord()

@discord.command("slash-example")
def chat_command(interaction: types.ChatInteraction) -> types.InteractionResponse:
    return types.InteractionResponse(
            type=types.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                    data=types.InteractionCallbackDataMessages(
            data=types.InteractionCallbackDataMessages(
                content="Hello, World!"
            )
        )
chat_command.description = "Say hello via a slash command"

discord.init_app(app)
```
