from typing import Any
from aiogram.fsm.state import State
from aiogram.types import InlineKeyboardButton

from aiogram_renderer.core.callback_data import ComeToCD, ModeCD
from aiogram_renderer.types.data import RendererData
from aiogram_renderer.widgets import Widget


from aiogram_renderer.widgets.widget import Condition


class InlineButton(Widget):
    __slots__ = ("text", "callback_data", "url")

    def __init__(self, text, callback_data=None, url=None, show_on: Condition = None):
        self.text = text
        self.callback_data = callback_data
        self.url = url
        super().__init__(show_on=show_on)

    async def _render(self, data, *args, **kwargs) -> InlineKeyboardButton | None:
        return InlineKeyboardButton(
            text=await self.resolve_value(self.text, data),
            callback_data=await self.resolve_value(self.callback_data, data),
            url=await self.resolve_value(self.url, data),
        )


class Mode(InlineButton):
    __slots__ = ("name",)

    def __init__(self, name: str, show_on: Condition = None):
        self.name = name
        super().__init__(text=name, callback_data=ModeCD(name=name).pack(), show_on=show_on)

    async def _render(self, data: dict[str, Any], rdata: RendererData, **kwargs) -> Any:
        """
        Берем активное [0] значение режима из fsm
        :param data: данные окна
        """
        return InlineKeyboardButton(text=rdata.modes[self.name][0], callback_data=self.callback_data)


class Delete(InlineButton):
    __slots__ = ()

    def __init__(self, text: str, show_on: Condition = None):
        super().__init__(text=text, callback_data="__delete__", show_on=show_on)


class Disable(InlineButton):
    __slots__ = ()

    def __init__(self, text: str, show_on: Condition = None):
        super().__init__(text=text, callback_data="__disable__", show_on=show_on)


class ComeTo(InlineButton):
    __slots__ = ()

    def __init__(self, text: str, state: State, show_on: Condition = None):
        super().__init__(
            text=text, callback_data=ComeToCD(group=state.group.__name__, state=state._state).pack(), show_on=show_on
        )
