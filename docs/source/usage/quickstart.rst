
Quickstart
==========

This page gives a brief introduction to the library.

A Simple Bot
------------

This is the finished product for our example bot. We'll go through it step by step.

.. code-block:: python

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
    chat_command.description = "Say Hello via a slash command"

    discord.init_app(app)

First, the imports.

.. code-block:: python

    import os

    from flask import Flask

    from flask_discord_interactions import Discord
    from flask_discord_interactions import discord_types as types

1. :code:`os` is imported for environment variables.

2. :code:`flask.Flask` is imported because shockingly we need flask for our flask extension.

3. :code:`flask_discord_interactions.Discord` and :code:`flask_discord_interactions.discord_types` are what we're going to use to define out bots behaviour.

Next, initializing our :code:`Flask` app.

.. code-block:: python

    app = Flask(__name__)
    app.config['DISCORD_PUBLIC_KEY'] = os.environ['DISCORD_PUBLIC_KEY']
    app.config['DISCORD_CLIENT_ID'] = os.environ['DISCORD_CLIENT_ID']
    app.config['DISCORD_CLIENT_SECRET'] = os.environ['DISCORD_CLIENT_SECRET']

We initialize our :code:`Flask` application and define three configuration values. The `Discord Getting Started <https://discord.com/developers/docs/getting-started>`_ page has all the info you need to actually get these values.
It goes without saying that you should not commit sensitive data to source control (such as :code:`DISCORD_CLIENT_SECRET`).

1. We need :code:`DISCORD_PUBLIC_KEY` to authenticate incoming requests.

2. We need :code:`DISCORD_CLIENT_ID` and :code:`DISCORD_CLIENT_SECRET` in order to authenticate with the Discord API to create our commands.

.. code-block:: python

    discord = Discord()
    
In order to define our commands, we need a :ref:`Discord` instance.

.. code-block:: python

    @discord.command("slash-example")
    def chat_command(interaction: types.ChatInteraction) -> types.InteractionResponse:
        ...

There's actually a lot going on in this little snippet.

:code:`@discord.command("slack-example")` applies a decorator to the :code:`chat_command` function. This decorator knows how to construct the correct type of command based on the functions type hints. This function has declared that it takes a :class:`~flask_discord_interactions.discord_types.ChatInteraction` parameter, and based on that the library knows to construct a `Slash Command <https://discord.com/developers/docs/interactions/application-commands#slash-commands>`_.

Since a name was passed to :meth:`~flask_discord_interactions.discord.Discord.command`, that name will be used to trigger the action, in this case "/slack-example". If no name was given, it would default to the functions name: "chat_command".

.. code-block:: python

    def chat_command(interaction: types.ChatInteraction) -> types.InteractionResponse:
        return types.InteractionResponse(
                type=types.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                        data=types.InteractionCallbackDataMessages(
                data=types.InteractionCallbackDataMessages(
                    content="Hello, World!"
                )
            )

As of the current version of the project, this is where the convenience features end. 

1. The command is passed a :class:`flask_discord_interactions.discord_types.ChatInteraction` instance. This is a just the data we were sent from discord, serialized into a :class:`~dataclasses.dataclass`.

2. A command must return an :class:`flask_discord_interactions.discord_types.InteractionResponse` instance, and you must construct this manually.

.. code-block:: python

    chat_command.description = "Say Hello via a slash command"

After a slash command has been defined, you may add a description to it.

.. code-block:: python

    discord.init_app(app)

Finally, call :meth:`flask_discord_interactions.discord.Discord.init_app` to attach the "/discord/interactions" endpoint to your app, and submit your commands to Discord.
