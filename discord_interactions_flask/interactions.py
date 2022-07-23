from dataclasses import dataclass
from typing import Union, List

from discord_interactions_flask.discord_types import (
    Interaction,
    InteractionData,
    MessageComponent,
)

# TODO: These can have their own definition
ChatData = InteractionData
UserData = InteractionData
MessageData = InteractionData
# If we do give them their own definition
# InteractionData = Union[ChatData, UserData, MessageData, ...]


@dataclass
class ChatInteraction(Interaction):
    data: ChatData


@dataclass
class UserInteraction(Interaction):
    data: UserData


@dataclass
class MessageInteraction(Interaction):
    data: MessageData


# TODO: These can have their own definition
ButtonData = MessageComponent
TextInputData = MessageComponent


@dataclass
class SelectMenuData(MessageComponent):
    values: List[str]


@dataclass
class ButtonInteraction(Interaction):
    data: ButtonData


@dataclass
class SelectMenuInteraction(Interaction):
    data: SelectMenuData


@dataclass
class TextInputInteraction(Interaction):
    data: TextInputData


CommandInteraction = Union[ChatInteraction, UserInteraction, MessageInteraction]
ComponentInteraction = Union[
    ButtonInteraction, SelectMenuInteraction, TextInputInteraction
]
