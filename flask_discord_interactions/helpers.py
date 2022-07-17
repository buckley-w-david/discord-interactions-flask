from typing import Optional
from flask_discord_interactions.discord_types import (
    InteractionResponse,
    InteractionCallbackType,
    InteractionCallbackDataMessage,
)


def content_response(content: str, flags: Optional[int] = None) -> InteractionResponse:
    return InteractionResponse(
        type=InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
        data=InteractionCallbackDataMessage(content=content, flags=flags),
    )
