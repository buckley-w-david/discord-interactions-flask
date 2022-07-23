__version__ = "0.2.0"

from discord_interactions_flask.discord import Discord
from discord_interactions_flask.discord_types import (
    InteractionResponse,
)
from discord_interactions_flask.interactions import (
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
# TODO: Should we attempt to persist component handlers across invocations? It would likely require pickeling the functions and storing them somewhere
# TODO: Should we also try to offer a more streamlined decorator that automatically parses and creates slash command arguments from type signatures of function params?

# TODO: Better ergonomics on response
# 1. A command should be able to just return a str to make the simple case easy
# 2. Decide how to handle deferred-type responses
# 3. More helpers?
