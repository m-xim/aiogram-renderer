from typing import Any
from aiogram.types import KeyboardButton
from widgets.keyboard.reply.button import ReplyButton
from widgets.widget import Widget


class ReplyGroup(Widget):
    __slots__ = ("buttons", "width")

    def __init__(self, *buttons: ReplyButton, width: int = 1, when: str = None):
        assert width >= 1, ValueError("Минимальная ширина ReplyKeyboard 1")
        assert width <= 12, ValueError("Максимальная ширина ReplyKeyboard строки 12")
        self.buttons = list(buttons)
        self.width = width
        super().__init__(when=when)

    async def assemble(self, data: dict[str, Any], *args, **kwargs) -> list[list[KeyboardButton]]:
        # Собираем объект группы кнопок Telegram
        buttons_rows = [[]]
        k = 0
        j = 0
        for button in self.buttons:
            # Если when в ключах data, то делаем проверку
            if button.when in data.keys():
                # Если when = False, не собираем кнопку
                if not data[button.when]:
                    continue

            button_obj = await button.assemble(data=data, *args, **kwargs)
            if j % self.width == 0 and j != 0:
                buttons_rows.append([button_obj])
                k += 1
            else:
                buttons_rows[k].append(button_obj)
            j += 1
        return buttons_rows


class ReplyRow(ReplyGroup):
    __slots__ = ()

    def __init__(self, *buttons: ReplyButton, when: str = None):
        super().__init__(*buttons, width=len(buttons), when=when)


class ReplyColumn(ReplyGroup):
    __slots__ = ()

    def __init__(self, *buttons: ReplyButton, when: str = None):
        super().__init__(*buttons, width=1, when=when)
