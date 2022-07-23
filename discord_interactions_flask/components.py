from typing import Union, Callable, Optional

from discord_interactions_flask import discord_types as types
from discord_interactions_flask import interactions

ButtonFunction = Callable[[interactions.ButtonInteraction], types.InteractionResponse]
TextInputFunction = Callable[
    [interactions.TextInputInteraction], types.InteractionResponse
]
SelectMenuFunction = Callable[
    [interactions.TextInputInteraction], types.InteractionResponse
]


class Button(types.Button):
    def __init__(
        self,
        *args,
        interaction_handler: Optional[ButtonFunction] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._func = interaction_handler

    def handler(self, f: ButtonFunction):
        self._func = f
        return f

    @property
    def interaction_handler(self) -> Optional[ButtonFunction]:
        return self._func

    @interaction_handler.setter
    def interaction_handler(
        self, f: Callable[[interactions.ButtonInteraction], types.InteractionResponse]
    ):
        self.handler(f)

    def __call__(
        self, interaction: interactions.ButtonInteraction
    ) -> types.InteractionResponse:
        if self._func is None:
            raise ValueError("This Button was not assigned a handler")
        return self._func(interaction)


class TextInput(types.TextInput):
    def __init__(
        self,
        *args,
        interaction_handler: Optional[TextInputFunction] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._func = interaction_handler

    def handler(self, f: TextInputFunction):
        self._func = f
        return f

    @property
    def interaction_handler(self) -> Optional[TextInputFunction]:
        return self._func

    @interaction_handler.setter
    def interaction_handler(
        self,
        f: Callable[[interactions.TextInputInteraction], types.InteractionResponse],
    ):
        self.handler(f)

    def __call__(
        self, interaction: interactions.TextInputInteraction
    ) -> types.InteractionResponse:
        if self._func is None:
            raise ValueError("This TextInput was not assigned a handler")
        return self._func(interaction)


class SelectMenu(types.SelectMenu):
    def __init__(
        self,
        *args,
        interaction_handler: Optional[SelectMenuFunction] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._func = interaction_handler

    def handler(self, f: SelectMenuFunction):
        self._func = f
        return f

    @property
    def interaction_handler(self) -> Optional[SelectMenuFunction]:
        return self._func

    @interaction_handler.setter
    def interaction_handler(
        self,
        f: Callable[[interactions.SelectMenuInteraction], types.InteractionResponse],
    ):
        self.handler(f)

    def __call__(
        self, interaction: interactions.SelectMenuInteraction
    ) -> types.InteractionResponse:
        if self._func is None:
            raise ValueError("This SelectMenu was not assigned a handler")
        return self._func(interaction)


Component = Union[Button, TextInput, SelectMenu]
