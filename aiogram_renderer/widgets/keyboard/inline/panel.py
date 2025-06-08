from typing import Any
from aiogram.types import InlineKeyboardButton

from aiogram_renderer.types.data import RendererData
from aiogram_renderer.widgets import Widget
from aiogram_renderer.widgets.keyboard.inline.button import InlineButton
from aiogram_renderer.widgets.widget import Condition


class InlinePanel(Widget):
    __slots__ = ("buttons", "width")

    def __init__(self, *buttons: InlineButton, width: int = 1, show_on: Condition = None):
        if width < 1:
            raise ValueError("Ширина группы должна быть не меньше 1")
        if width > 8:
            raise ValueError("У Telegram ограничение на длину InlineKeyboard - 8 кнопок")
        if len(buttons) / width > 100:
            raise ValueError("У Telegram ограничение на высоту InlineKeyboard - 100 кнопок")

        self.buttons = buttons
        self.width = width
        super().__init__(show_on=show_on)

    async def _render(self, data: dict[str, Any], rdata: RendererData, **kwargs) -> list[list[InlineKeyboardButton]]:
        # Собираем объект группы кнопок Telegram
        buttons_rows = [[]]
        k = 0
        j = 0
        for button in self.buttons:
            button_obj = await button.render(data=data, **kwargs)
            if j % self.width == 0 and j != 0:
                buttons_rows.append([button_obj])
                k += 1
            else:
                buttons_rows[k].append(button_obj)
            j += 1

        return buttons_rows


class Row(InlinePanel):
    __slots__ = ()

    def __init__(self, *buttons: InlineButton, show_on: Condition = None):
        super().__init__(*buttons, width=len(buttons), show_on=show_on)


class Column(InlinePanel):
    __slots__ = ()

    def __init__(self, *buttons: InlineButton, show_on: Condition = None):
        super().__init__(*buttons, width=1, show_on=show_on)
