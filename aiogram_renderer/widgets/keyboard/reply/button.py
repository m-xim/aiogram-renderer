from aiogram.types import KeyboardButton

from aiogram_renderer.types.data import RendererData
from aiogram_renderer.widgets import Widget
from aiogram_renderer.widgets.widget import Value


class ReplyButton(Widget):
    __slots__ = ("text",)

    def __init__(self, text: Value, show_on: str = None):
        self.text = text
        super().__init__(show_on=show_on)

    async def _render(self, data, rdata: RendererData, **kwargs) -> KeyboardButton | None:
        return KeyboardButton(text=await self.resolve_value(self.text, data))


class ReplyMode(ReplyButton):
    __slots__ = ("name",)

    def __init__(self, name: Value, show_on: str = None):
        """
        Виджет режима бота на ReplyKeyboard, на вход задаем название режима, который хоти видеть,
        стоит учесть что при переключении режима Mode - ReplyMode не будет меняться,
        для этого вам нужно писать свой хендлер и доп. логику
        :param name: название режима
        :param show_on: фильтр видимости виджета
        """
        self.name = name
        # Для обработки используется системный хендлер с bot.modes.values
        super().__init__(text=name, show_on=show_on)

    async def _render(self, data, rdata: RendererData, **kwargs):
        """
        Берем активное [0] значение режима из fsm
        :param data: данные окна
        """
        return KeyboardButton(text=rdata.modes[self.name][0])
