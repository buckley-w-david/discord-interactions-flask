from discord_interactions_flask import discord_types as types
from discord_interactions_flask.discord_types import (
    ActionRow,
    Button,
    SelectMenu,
    TextInput,
)


def test_button():
    obj = {"custom_id": "button", "label": "label", "type": 2, "style": 1}

    button = Button.load(obj)
    assert button.type is types.ComponentType.BUTTON
    assert button.style is types.ButtonStyle.PRIMARY


def test_select_menu():
    obj = {
        "type": 3,
        "custom_id": "abc123",
        "options": [{"label": "test", "value": "5"}],
    }

    message = SelectMenu.load(obj)
    assert message.type is types.ComponentType.SELECT_MENU
    assert message.custom_id == "abc123"
    assert type(message.options[0]) is types.SelectOption
    assert message.options[0].label == "test"
    assert message.options[0].value == "5"


def test_text_input():
    obj = {
        "type": 4,
        "custom_id": "abc123",
        "style": 1,
        "label": "thing",
    }

    message = TextInput.load(obj)
    assert message.type is types.ComponentType.TEXT_INPUT
    assert message.custom_id == "abc123"
    assert message.style is types.TextInputStyle.SHORT
    assert message.label == "thing"


def test_action_row():
    row = {"type": 1, "components": []}

    row = ActionRow.load(row)
    assert row.type is types.ComponentType.ACTION_ROW
    assert not row.components


def test_action_row_with_components():
    row = {
        "type": 1,
        "components": [
            {"type": 2, "label": "Click me!", "style": 1, "custom_id": "click_one"},
            {"type": 4, "label": "Text Input!", "style": 1, "custom_id": "text_one"},
        ],
    }

    row = ActionRow.load(row)
    assert row.type is types.ComponentType.ACTION_ROW
    assert len(row.components) == 2
    assert type(row.components[0]) is Button
    assert type(row.components[1]) is TextInput
