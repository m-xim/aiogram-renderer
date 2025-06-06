from typing import Any
from aiogram.types import KeyboardButton
from aiogram_renderer.widgets.keyboard.reply import ReplyButton
from aiogram_renderer.widgets import Widget


class ReplyPanel(Widget):
    __slots__ = ("buttons", "width")

    def __init__(self, *buttons: ReplyButton, width: int = 1, show_on: str = None):
        if width < 1:
            raise ValueError("Ширина группы должна б��ть не меньше 1")
        if width > 12:
            raise ValueError("У Telegram ограничение на длину ReplyKeyboard - 12 кнопок")
        self.buttons = list(buttons)
        self.width = width
        super().__init__(show_on=show_on)

    async def _render(self, data: dict[str, Any], **kwargs) -> list[list[KeyboardButton]]:
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


class ReplyRow(ReplyPanel):
    def __init__(self, *buttons: ReplyButton, show_on: str = None):
        super().__init__(*buttons, width=len(buttons), show_on=show_on)


class ReplyColumn(ReplyPanel):
    def __init__(self, *buttons: ReplyButton, show_on: str = None):
        super().__init__(*buttons, width=1, show_on=show_on)
