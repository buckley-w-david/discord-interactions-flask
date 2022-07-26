from unittest.mock import MagicMock

from discord_interactions_flask.command import (
    ChatMetaCommand,
    SubCommand,
    CommandGroup,
    ChatCommand,
)
from discord_interactions_flask.discord_types import (
    ApplicationCommandOption,
    ApplicationCommandOptionType,
    ApplicationCommandOptionChoice,
)

# Optional elements are explicitly returned as `None` from spec()
# For our purposes though, that's an implementation detail and doesn't really matter
# This method is just to clean up those `None` valued entries to declutter tests
def compact(obj):
    if isinstance(obj, dict):
        return {k: compact(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [compact(v) for v in obj]
    else:
        return obj


class TestSpec():
    def test_chat_command_spec(self):
        command = ChatCommand(
            name="blep", description="Send a random adorable animal photo"
        )
        command.add_option(
            ApplicationCommandOption(
                type=ApplicationCommandOptionType.STRING,
                name="animal",
                description="The type of animal",
                required=True,
                choices=[
                    ApplicationCommandOptionChoice(
                        name="Dog",
                        value="animal_dog",
                    ),
                    ApplicationCommandOptionChoice(
                        name="Cat",
                        value="animal_cat",
                    ),
                    ApplicationCommandOptionChoice(
                        name="Penguin",
                        value="animal_penguin",
                    ),
                ],
            )
        )
        command.add_option(
            ApplicationCommandOption(
                type=ApplicationCommandOptionType.BOOLEAN,
                name="only_smol",
                description="Whether to show only baby animals",
                required=False,
            )
        )
        spec = compact(command.spec())
        assert spec == {
            "name": "blep",
            "type": 1,
            "description": "Send a random adorable animal photo",
            "options": [
                {
                    "name": "animal",
                    "description": "The type of animal",
                    "type": 3,
                    "required": True,
                    "choices": [
                        {"name": "Dog", "value": "animal_dog"},
                        {"name": "Cat", "value": "animal_cat"},
                        {"name": "Penguin", "value": "animal_penguin"},
                    ],
                },
                {
                    "name": "only_smol",
                    "description": "Whether to show only baby animals",
                    "type": 5,
                    "required": False,
                },
            ],
        }


    def test_meta_command_spec(self):
        command = ChatMetaCommand(
            name="permissions",
            description="Get or edit permissions for a user or a role",
            _children={
                "user": CommandGroup(
                    name="user",
                    description="Get or edit permissions for a user",
                    _subcommands={
                        "get": SubCommand(
                            name="get",
                            description="Get permissions for a user",
                            options=[
                                ApplicationCommandOption(
                                    type=ApplicationCommandOptionType.USER,
                                    name="user",
                                    description="The user to get",
                                    required=True,
                                ),
                                ApplicationCommandOption(
                                    type=ApplicationCommandOptionType.CHANNEL,
                                    name="channel",
                                    description="The channel permissions to get. If omitted, the guild permissions will be returned",
                                    required=False,
                                ),
                            ],
                        ),
                        "edit": SubCommand(
                            name="edit",
                            description="Edit permissions for a user",
                            options=[
                                ApplicationCommandOption(
                                    type=ApplicationCommandOptionType.USER,
                                    name="user",
                                    description="The user to edit",
                                    required=True,
                                ),
                                ApplicationCommandOption(
                                    type=ApplicationCommandOptionType.CHANNEL,
                                    name="channel",
                                    description="The channel permissions to edit. If omitted, the guild permissions will be edited",
                                    required=False,
                                ),
                            ],
                        ),
                    },
                ),
                "role": CommandGroup(
                    name="role",
                    description="Get or edit permissions for a role",
                    _subcommands={
                        "get": SubCommand(
                            name="get",
                            description="Get permissions for a role",
                            options=[
                                ApplicationCommandOption(
                                    type=ApplicationCommandOptionType.ROLE,
                                    name="role",
                                    description="The role to get",
                                    required=True,
                                ),
                                ApplicationCommandOption(
                                    type=ApplicationCommandOptionType.CHANNEL,
                                    name="channel",
                                    description="The channel permissions to get. If omitted, the guild permissions will be returned",
                                    required=False,
                                ),
                            ],
                        ),
                        "edit": SubCommand(
                            name="edit",
                            description="Edit permissions for a role",
                            options=[
                                ApplicationCommandOption(
                                    type=ApplicationCommandOptionType.ROLE,
                                    name="role",
                                    description="The role to edit",
                                    required=True,
                                ),
                                ApplicationCommandOption(
                                    type=ApplicationCommandOptionType.CHANNEL,
                                    name="channel",
                                    description="The channel permissions to edit. If omitted, the guild permissions will be edited",
                                    required=False,
                                ),
                            ],
                        ),
                    },
                ),
            },
        )
        spec = compact(command.spec())
        assert spec == {
            "name": "permissions",
            "description": "Get or edit permissions for a user or a role",
            "type": 1,
            "options": [
                {
                    "name": "user",
                    "description": "Get or edit permissions for a user",
                    "type": 2,
                    "options": [
                        {
                            "name": "get",
                            "description": "Get permissions for a user",
                            "type": 1,
                            "options": [
                                {
                                    "name": "user",
                                    "description": "The user to get",
                                    "type": 6,
                                    "required": True,
                                },
                                {
                                    "name": "channel",
                                    "description": "The channel permissions to get. If omitted, the guild permissions will be returned",
                                    "type": 7,
                                    "required": False,
                                },
                            ],
                        },
                        {
                            "name": "edit",
                            "description": "Edit permissions for a user",
                            "type": 1,
                            "options": [
                                {
                                    "name": "user",
                                    "description": "The user to edit",
                                    "type": 6,
                                    "required": True,
                                },
                                {
                                    "name": "channel",
                                    "description": "The channel permissions to edit. If omitted, the guild permissions will be edited",
                                    "type": 7,
                                    "required": False,
                                },
                            ],
                        },
                    ],
                },
                {
                    "name": "role",
                    "description": "Get or edit permissions for a role",
                    "type": 2,
                    "options": [
                        {
                            "name": "get",
                            "description": "Get permissions for a role",
                            "type": 1,
                            "options": [
                                {
                                    "name": "role",
                                    "description": "The role to get",
                                    "type": 8,
                                    "required": True,
                                },
                                {
                                    "name": "channel",
                                    "description": "The channel permissions to get. If omitted, the guild permissions will be returned",
                                    "type": 7,
                                    "required": False,
                                },
                            ],
                        },
                        {
                            "name": "edit",
                            "description": "Edit permissions for a role",
                            "type": 1,
                            "options": [
                                {
                                    "name": "role",
                                    "description": "The role to edit",
                                    "type": 8,
                                    "required": True,
                                },
                                {
                                    "name": "channel",
                                    "description": "The channel permissions to edit. If omitted, the guild permissions will be edited",
                                    "type": 7,
                                    "required": False,
                                },
                            ],
                        },
                    ],
                },
            ],
        }


class TestMetaCommand:
    def test_meta_delegates_to_subcommand(self, meta_subcommand_interaction):
        mock = MagicMock()

        sub_name = meta_subcommand_interaction.data.options[0].name

        subcommand = SubCommand(name=sub_name, description=sub_name)
        subcommand.interaction_handler = mock
        command = ChatMetaCommand(
            name="test_meta", description="test_meta", _children={sub_name: subcommand}
        )

        command(meta_subcommand_interaction)

        mock.assert_called_once_with(meta_subcommand_interaction)

    def test_meta_delegates_to_group(self, meta_group_interaction):
        mock = MagicMock()

        group_name = meta_group_interaction.data.options[0].name
        sub_name = meta_group_interaction.data.options[0].options[0].name

        subcommand = SubCommand(name=sub_name, description=sub_name)
        subcommand.interaction_handler = mock
        group = CommandGroup(
            name=group_name, description=group_name, _subcommands={sub_name: subcommand}
        )
        command = ChatMetaCommand(
            name="test_meta", description="test_meta", _children={group_name: group}
        )

        command(meta_group_interaction)

        mock.assert_called_once_with(meta_group_interaction)
