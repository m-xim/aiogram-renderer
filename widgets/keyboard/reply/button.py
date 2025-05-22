from typing import Any
from aiogram.types import KeyboardButton
from widgets.widget import Widget


class ReplyButton(Widget):
    __slots__ = ("text",)

    def __init__(self, text: str, when: str = None):
        self.text = text
        super().__init__(when=when)

    async def assemble(self, data: dict[str, Any], *args, **kwargs) -> KeyboardButton | None:
        if self.when in data.keys():
            # Если when = False, не собираем кнопку и возвращаем None
            if not data[self.when]:
                return None

        text = self.text

        # Форматируем по data, если там заданы ключи {key}
        for key, value in data.items():
            if "{" + key + "}" in text:
                text = text.replace("{" + key + "}", value)

        return KeyboardButton(text=text)


class ReplyMode(ReplyButton):
    __slots__ = ("name",)

    def __init__(self, name: str, when: str = None):
        self.name = name
        # Для обработки используется системный хендлер с bot.modes.values
        super().__init__(text=name, when=when)

    async def assemble(self, data: dict[str, Any], modes: dict[str, Any]):
        """
        Берем активное [0] значение режима из fsm
        :param data: данные окна
        """
        if self.when in data.keys():
            # Если when = False, не собираем кнопку и возвращаем None
            if not data[self.when]:
                return None

        text = modes[self.name][0]
        return KeyboardButton(text=text)
