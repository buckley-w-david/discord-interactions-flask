from flask_discord_interactions.discord_types import (
    InteractionResponse,
    InteractionCallbackType,
    InteractionCallbackDataMessage,
)


def content_response(content: str) -> InteractionResponse:
    return InteractionResponse(
        type=InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
        data=InteractionCallbackDataMessage(content=content),
    )
