from typing import Any
from aiogram.fsm.state import State
from aiogram.types import InlineKeyboardButton
from widgets.widget import Widget


class Button(Widget):
    __slots__ = ("text", "data")

    def __init__(self, text: str, data: str, when: str = None):
        self.text = text
        self.data = data
        super().__init__(when=when)

    async def assemble(self, data: dict[str, Any], *args, **kwargs) -> InlineKeyboardButton | None:
        text = self.text
        btn_data = self.data

        if self.when in data.keys():
            # Если when = False, не собираем кнопку и возвращаем None
            if not data[self.when]:
                return None

        # Форматируем по data, если там заданы ключи {key}
        for key, value in data.items():
            if "{" + key + "}" in text:
                text = text.replace("{" + key + "}", value)
            if "{" + key + "}" in btn_data:
                btn_data = btn_data.replace("{" + key + "}", value)

        return InlineKeyboardButton(text=text, callback_data=btn_data)


class Mode(Button):
    __slots__ = ("name",)

    def __init__(self, name: str, when: str = None):
        self.name = name
        super().__init__(text=name, data=f"__mode__:{name}", when=when)

    async def assemble(self, data: dict[str, Any], modes: dict[str, Any]) -> InlineKeyboardButton | None:
        """
        Берем активное [0] значение режима из fsm
        :param data: данные окна
        """
        if self.when in data.keys():
            # Если when = False, не собираем кнопку и возвращаем None
            if not data[self.when]:
                return None

        text = modes[self.name][0]
        return InlineKeyboardButton(text=text, callback_data=self.data)


class Delete(Button):
    __slots__ = ()

    def __init__(self, text: str, when: str = None):
        super().__init__(text=text, data=f"__delete__", when=when)


class Disable(Button):
    __slots__ = ()

    def __init__(self, text: str, when: str = None):
        super().__init__(text=text, data=f"__disable__", when=when)


class SwitchTo(Button):
    __slots__ = ()

    def __init__(self, text: str, state: State, when: str = None):
        super().__init__(text=text, data=f"__switch_to__:{state.state}", when=when)
