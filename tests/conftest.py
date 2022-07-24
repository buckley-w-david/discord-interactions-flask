import pytest

from discord_interactions_flask.interactions import ChatInteraction, ChatData
from discord_interactions_flask.discord_types import (
    InteractionType,
    CommandType,
    ApplicationCommandInteractionDataOption,
    ApplicationCommandOptionType,
)


@pytest.fixture
def meta_subcommand_interaction():
    return ChatInteraction(
        id="meta_chat_id",
        application_id="meta_chat_application_id",
        type=InteractionType.APPLICATION_COMMAND,
        token="meta_chat_token",
        version=1,
        data=ChatData(
            id="meta_chat_data_id",
            name="meta_chat_command_name",
            type=CommandType.CHAT,
            options=[
                ApplicationCommandInteractionDataOption(
                    name="meta_chat_sub_1",
                    type=ApplicationCommandOptionType.SUB_COMMAND,
                ),
            ],
        ),
        guild_id="meta_chat_guild_id",
        channel_id="meta_chat_channel_id",
    )


@pytest.fixture
def meta_group_interaction():
    return ChatInteraction(
        id="meta_chat_id",
        application_id="meta_chat_application_id",
        type=InteractionType.APPLICATION_COMMAND,
        token="meta_chat_token",
        version=1,
        data=ChatData(
            id="meta_chat_data_id",
            name="meta_chat_command_name",
            type=CommandType.CHAT,
            options=[
                ApplicationCommandInteractionDataOption(
                    name="meta_chat_group_1",
                    type=ApplicationCommandOptionType.SUB_COMMAND_GROUP,
                    options=[
                        ApplicationCommandInteractionDataOption(
                            name="meta_chat_sub_1",
                            type=ApplicationCommandOptionType.SUB_COMMAND,
                        ),
                    ],
                ),
            ],
        ),
        guild_id="meta_chat_guild_id",
        channel_id="meta_chat_channel_id",
    )
