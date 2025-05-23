from typing import Any
from aiogram.types import InlineKeyboardButton
from widgets.keyboard.inline.button import Button
from widgets.widget import Widget


class Group(Widget):
    __slots__ = ("buttons", "width")

    def __init__(self, *buttons: Button, width: int = 1, when: str = None):
        # Минимальная ширина 1
        assert width >= 1, ValueError("Widget width must be greater than zero")
        # Максимальная ширина inlineKeyboard строки 8 (ограничение Telegram)
        assert width <= 8, ValueError("There should be no more than 8 buttons in a Inline Buttons row")
        # Максимальная высота inlineKeyboard 100 (ограничение Telegram)
        assert len(buttons) / width <= 100, ValueError("No more than 100 buttons in a Inline Buttons column")
        self.buttons = list(buttons)
        self.width = width
        super().__init__(when=when)

    async def assemble(self, data: dict[str, Any], *args, **kwargs) -> list[list[InlineKeyboardButton]]:
        if self.when in data.keys():
            # Если when = False, не собираем группу
            if not data[self.when]:
                return [[]]

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


class Row(Group):
    __slots__ = ()

    def __init__(self, *buttons: Button, when: str = None):
        super().__init__(*buttons, width=len(buttons), when=when)


class Column(Group):
    __slots__ = ()

    def __init__(self, *buttons: Button, when: str = None):
        super().__init__(*buttons, width=1, when=when)


class DynamicGroup(Widget):
    __slots__ = ("name", "width", "height", "hide_control_buttons", "hide_number_pages")

    # Формат в fsm_data "name": {"page": 1, "text": ["text1", ...], "data": ["data1", ...]}
    def __init__(self, name: str, width: int = 1, height: int = 1,
                 hide_control_buttons: bool = False, hide_number_pages: bool = False, when: str = None):
        # Минимальная ширина и высота = 1
        assert width >= 1, ValueError("Widget width must be greater than zero")
        assert height >= 1, ValueError("Widget height must be greater than zero")
        # Максимальная ширина inlineKeyboard строки 8 (ограничение Telegram)
        assert width <= 8, ValueError("There should be no more than 8 buttons in a Inline Buttons row (Telegram)")
        assert height <= 99, ValueError("No more than 100 buttons in a Inline Buttons column (Telegram)")

        super().__init__(when=when)

        self.name = name
        self.width = width
        self.height = height
        self.hide_control_buttons = hide_control_buttons
        self.hide_number_pages = hide_number_pages

    async def assemble(self, data: dict[str, Any], *args, **kwargs) -> list[list[InlineKeyboardButton]]:
        if self.when in data.keys():
            # Если when = False, не собираем группу
            if not data[self.when]:
                return [[]]

        fsm_group: dict[str, Any] = data[self.name]
        page = fsm_group["page"]

        if len(fsm_group["text"]) != len(fsm_group["data"]):
            raise ValueError("Group data and text list should have the same length")

        count_buttons = len(fsm_group["text"])

        # Добавляем дополнительную страницу если при делении на число кнопок есть остатки
        last_page = count_buttons // (self.width * self.height)
        last_page = last_page + 1 if (count_buttons % (self.width * self.height)) > 0 else last_page

        # Проверяем не задали ли страницу больше чем есть
        if last_page < page:
            raise ValueError(f"There are not so many pages in the given data, max: {last_page} page")

        # Формируем набор кнопок, начиная с заданной страницы и заканчивая срезом по width, height
        start = self.width * self.height * (page - 1)
        trimmed_b_text = fsm_group["text"][start:start + (self.width * self.height)]
        trimmed_b_data = fsm_group["data"][start:start + (self.width * self.height)]

        buttons = [[]]
        row = 0
        for col, text, data in zip(range(count_buttons), trimmed_b_text, trimmed_b_data):
            button = InlineKeyboardButton(text=text, callback_data=data)

            if col % self.width == 0 and col != 0:
                buttons.append([button])
                row += 1
            else:
                buttons[row].append(button)

        # Формируем кнопки управления
        if (count_buttons > (self.width * self.height)) and (not self.hide_control_buttons):
            if self.hide_number_pages:
                if page == 1:
                    buttons.append([
                        InlineKeyboardButton(text=">", callback_data=f"__dgroup:{page + 1}:{self.name}"),
                    ])
                elif page == last_page:
                    buttons.append([
                        InlineKeyboardButton(text="<", callback_data=f"__dgroup:{page - 1}:{self.name}"),
                    ])
                else:
                    buttons.append([
                        InlineKeyboardButton(text="<", callback_data=f"__dgroup:{page - 1}:{self.name}"),
                        InlineKeyboardButton(text=">", callback_data=f"__dgroup:{page + 1}:{self.name}"),
                    ])
            else:
                if page == 1:
                    buttons.append([
                        InlineKeyboardButton(text="[ 1 ]", callback_data=f"__disable__"),
                        InlineKeyboardButton(text=">", callback_data=f"__dgroup:{page + 1}:{self.name}"),
                        InlineKeyboardButton(text=str(last_page), callback_data=f"__dgroup:{last_page}:{self.name}")
                    ])
                elif page == last_page:
                    buttons.append([
                        InlineKeyboardButton(text="1", callback_data=f"__dgroup:1:{self.name}"),
                        InlineKeyboardButton(text="<", callback_data=f"__dgroup:{page - 1}:{self.name}"),
                        InlineKeyboardButton(text=f"[ {last_page} ]", callback_data="__disable__"),
                    ])
                else:
                    buttons.append([
                        InlineKeyboardButton(text="1", callback_data=f"__dgroup:1:{self.name}"),
                        InlineKeyboardButton(text="<", callback_data=f"__dgroup:{page - 1}:{self.name}"),
                        InlineKeyboardButton(text=f"[ {page} ]", callback_data="__disable__"),
                        InlineKeyboardButton(text=">", callback_data=f"__dgroup:{page + 1}:{self.name}"),
                        InlineKeyboardButton(text=str(last_page), callback_data=f"__dgroup:{last_page}:{self.name}")
                    ])

        return buttons
