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

# TODO: Message Components
# TODO: I think meta commands might require descriptions
# TODO: Better logging and/or error handling
# TODO: Better ergonomics on response
#       Parse data out of different return signatures? str = regular message with no frills?
# TODO: Do I need a delete method on Discord, just for convenience. It's a PITA to remove a command as-is
#       There's a weird thought in here, keeping a db of commands and having like migrations and shit
# TODO: Your app can have a global CHAT_INPUT and USER command with the same name
#       Do I just decide to not support that?
#       I would have to break out each command type into separate dicts
# TODO: There should be a mechanism to opt-out of automatically init_commands-ing
