from unittest.mock import MagicMock

from discord_interactions_flask.command import ChatMetaCommand, SubCommand, CommandGroup, ChatCommand
from discord_interactions_flask.discord_types import ApplicationCommandOption, ApplicationCommandOptionType, ApplicationCommandOptionChoice

# Optional elements are explicitly returned as `None` from spec()
# For our purposes though, that's an implementation detail and doesn't really matter
# This method is just to clean up those `None` valued entries to declutter tests
def compact(obj):
    if isinstance(obj, dict):
        return {
            k: compact(v) for k, v in obj.items() if v is not None
        }
    elif isinstance(obj, list):
        return [
            compact(v) for v in obj
        ]
    else:
        return obj


def test_chat_command_spec():
    command = ChatCommand(name="blep", func=None)
    command.description = "Send a random adorable animal photo"
    command.add_option(
        ApplicationCommandOption(
            type=ApplicationCommandOptionType.STRING,
            name="animal",
            description= "The type of animal",
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
                )
            ]
        )
    )
    command.add_option(
        ApplicationCommandOption(
            type=ApplicationCommandOptionType.BOOLEAN,
            name="only_smol",
            description= "Whether to show only baby animals",
            required=False,
        )
    )
    spec = command.spec() 
    spec["options"] = compact(spec["options"])
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
                    {
                        "name": "Dog",
                        "value": "animal_dog"
                    },
                    {
                        "name": "Cat",
                        "value": "animal_cat"
                    },
                    {
                        "name": "Penguin",
                        "value": "animal_penguin"
                    }
                ]
            },
            {
                "name": "only_smol",
                "description": "Whether to show only baby animals",
                "type": 5,
                "required": False
            }
        ]
    }




class TestMetaCommand:
    def test_meta_delegates_to_subcommand(self, meta_subcommand_interaction):
        mock = MagicMock()

        sub_name = meta_subcommand_interaction.data.options[0].name

        subcommand = SubCommand(name=sub_name, func=mock)
        command = ChatMetaCommand(name="test_meta", children={ sub_name: subcommand })

        command(meta_subcommand_interaction)

        mock.assert_called_once_with(meta_subcommand_interaction)

    def test_meta_delegates_to_group(self, meta_group_interaction):
        mock = MagicMock()

        group_name = meta_group_interaction.data.options[0].name
        sub_name = meta_group_interaction.data.options[0].options[0].name

        subcommand = SubCommand(name=sub_name, func=mock)
        group = CommandGroup(
            name=group_name,
            subcommands={
                sub_name: subcommand
            }
        )
        command = ChatMetaCommand(name="test_meta", children={ group_name: group })

        command(meta_group_interaction)

        mock.assert_called_once_with(meta_group_interaction)
