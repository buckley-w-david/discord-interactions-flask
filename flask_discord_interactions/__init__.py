__version__ = "0.1.0"

from flask_discord_interactions.discord import Discord
from flask_discord_interactions.discord_types import (
    InteractionResponse,
)
from flask_discord_interactions.interactions import (
    ChatInteraction,
    UserInteraction,
    MessageInteraction,
)

# TODO: I want to make discord_types an implementation detail that users aren't expected to interact with,
# TODO: I think meta commands might require descriptions
# TODO: Better logging and/or error handling
#       Parse data out of different return signatures? str = regular message with no frills?
# TODO: built-in support for other InteractionCallbackType types
# TODO: Autocomplete support
# TODO: Document discord_types module
# TODO: Do I need a delete method on Discord, just for convenience. It's a PITA to remove a command as-is
#       There's a weird thought in here, keeping a db of commands and having like migrations and shit
# TODO: Your app can have a global CHAT_INPUT and USER command with the same name
#       Do I just decide to not support that?
#       I would have to break out each command type into separate dicts
# TODO: There should be a mechanism to opt-out of automatically init_commands-ing
# TODO: How do modals work?

# TODO: Message Components
# I think the best way forward here is all around concepts of "registering" handlers somehow within the functions themselves so they can dynamically include/exclude components with custom handling depending on whatever they want. Static handlers defined at start-time can't do that.
# This can coincide with making responses easier, as the response object could be what you register handlers on.
"""
@discord.command("slash-example")
def chat_command(interaction: interactions.ChatInteraction) -> types.InteractionResponse:
    @components.Button(...)
    def button(interaction) -> InteractionResponse:
      ...

    OR

    button = components.Button(...)
    button.handler = handle_button

    return types.InteractionResponse(
        type=types.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
        data=types.InteractionCallbackDataMessage(
            content="Hello, World!"
            components=[ActionRow(components=[button])]
        )
    )
chat_command.description = "Say Hello via a slash command"
"""

# Before sending the response back to Discord, we scan the `components` for the handlers so we can route future requests to them.
#
# TODO: Better ergonomics on response
# 1. A command should be able to just return a str to make the simple case easy
# 2. Decide how to handle deferred-type responses
# 3.
