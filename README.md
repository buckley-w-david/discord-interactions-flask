# discord-interactions-flask

A [Flask](https://github.com/pallets/flask/) extension to support interacting with [Discord Interactions](https://discord.com/developers/docs/interactions/application-commands).

Check out the [quickstart](https://docs.davidbuckley.ca/discord-interactions-flask/usage/quickstart.html) or the [examples directory](/examples) for an idea of how to use it.

```python
import os

from flask import Flask

from discord_interactions_flask import Discord
from discord_interactions_flask import helpers
from discord_interactions_flask.interactions ChatInteraction

app = Flask(__name__)
app.config['DISCORD_PUBLIC_KEY'] = os.environ['DISCORD_PUBLIC_KEY']
app.config['DISCORD_CLIENT_ID'] = os.environ['DISCORD_CLIENT_ID']
app.config['DISCORD_CLIENT_SECRET'] = os.environ['DISCORD_CLIENT_SECRET']

discord = Discord()

@discord.command("slash-example")
def chat_command(interaction: ChatInteraction) -> types.InteractionResponse:
    return helpers.content_response("Hello, World!")

chat_command.description = "Say hello via a slash command"

discord.init_app(app)
```
