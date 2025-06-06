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

    async def assemble(self, data: dict[str, Any], **kwargs) -> list[list[KeyboardButton]]:
        if self.show_on in data.keys():
            # Если when = False, не собираем группу
            if not data[self.show_on]:
                return [[]]

        # Собираем объект группы кнопок Telegram
        buttons_rows = [[]]
        k = 0
        j = 0
        for button in self.buttons:
            # Если when в ключах data, то делаем проверку
            if button.show_on in data.keys():
                # Если when = False, не собираем кнопку
                if not data[button.show_on]:
                    continue

            button_obj = await button.assemble(data=data, **kwargs)
            if j % self.width == 0 and j != 0:
                buttons_rows.append([button_obj])
                k += 1
            else:
                buttons_rows[k].append(button_obj)
            j += 1
        return buttons_rows


class ReplyRow(ReplyPanel):
    __slots__ = ()

    def __init__(self, *buttons: ReplyButton, show_on: str = None):
        super().__init__(*buttons, width=len(buttons), show_on=show_on)


class ReplyColumn(ReplyPanel):
    __slots__ = ()

    def __init__(self, *buttons: ReplyButton, show_on: str = None):
        super().__init__(*buttons, width=1, show_on=show_on)
