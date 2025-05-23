from abc import ABC
from aiogram.fsm.state import State
from typing import Any
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from widgets.keyboard.inline.button import Button
from widgets.keyboard.inline.group import Group, DynamicGroup
from widgets.keyboard.reply.button import ReplyButton
from widgets.keyboard.reply.group import ReplyGroup
from widgets.text import Text, Multi
from widgets.widget import Widget


class ABCWindow(ABC):
    __slots__ = ('widgets',)

    def __init__(self, *widgets: Widget):
        self.widgets = list(widgets)

    async def gen_reply_markup(self, data: dict[str, Any], modes: dict[str, Any]) -> Any:
        keyboard = []
        button_objs = []
        has_groups = False
        is_inline_keyboard = False

        for widget in self.widgets:
            if isinstance(widget, (Button, Group, DynamicGroup, ReplyButton, ReplyGroup)):
                if isinstance(widget, (Group, ReplyGroup, DynamicGroup)):
                    has_groups = True
                if isinstance(widget, (Button, Group, DynamicGroup)):
                    is_inline_keyboard = True

                button_objs.append(widget)

        # Если есть виджет Group, то добавляем его строки в клавиатуру
        if has_groups:
            for b in button_objs:
                btn_object = await b.assemble(data=data, modes=modes)
                # Если после сборки не None (тоесть кнопка видна, то добавляем ее в клавиатуру)
                if btn_object is not None:
                    # Если Group, то добавляем его строки в клавиатуру
                    if isinstance(b, (Group, ReplyGroup, DynamicGroup)):
                        for button_row in btn_object:
                            keyboard.append(button_row)
                    else:  # Иначе, если Button, то добавляем его в новую строку
                        keyboard.append([btn_object])

        # Если Group нет, то все кнопки устанавливаются в одной строке
        elif button_objs:
            keyboard.append([])
            for b in button_objs:
                button_obj = await b.assemble(data=data, modes=modes)
                keyboard[0].append(button_obj)

        # Если Group нет и кнопок нет, то возвращаем None
        else:
            return None

        # Если есть клавиатура, задаем ReplyMarkup
        if is_inline_keyboard:
            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        else:
            reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

        return reply_markup

    async def gen_text(self, data: dict[str, Any]) -> str:
        text = ""
        for widget in self.widgets:
            if isinstance(widget, (Text, Multi)):
                text += await widget.assemble(data=data)
        return text

    async def assemble(self, data: dict[str, Any], modes: dict[str, Any]) -> tuple[str, Any]:
        reply_markup = await self.gen_reply_markup(data=data, modes=modes)
        text = await self.gen_text(data=data)
        return text, reply_markup


class Window(ABCWindow):
    __slots__ = ('state',)

    def __init__(self, *widgets: Widget, state: State):
        # raise ValueError("Progress bar with this name already exists")
        # if isinstance(w, (Button, DynamicGroup, Group)) and keyboard_type == keyboard_type.REPLY:
        #     raise ValueError("You set inline buttons, in reply keyboard")
        # elif isinstance(w, (ReplyButton, ReplyGroup)) and keyboard_type == keyboard_type.INLINE:
        #     raise ValueError("You set reply buttons, in inline keyboard")
        # assert w.fsm_name not in dgroups_names, ValueError("DynamicGroups must have unique names")
        # # Проверяем чтобы был хотя бы один текстовый виджет
        # assert len(texts) >= 1, ValueError("There must be at least one Text widget in")
        # # Проверяем чтобы было не более одной MediaGroup или не более одного файлового виджета
        # assert len(files) <= 1, ValueError("There can be only one MediaGroup|File widget in")
        # if files:
        #     if (keyboard_type is not None) and isinstance(files[0], MediaGroup):
        #         raise ValueError("You can't use keyboard with media_group")
        self.state = state
        super().__init__(*widgets)


class Alert(ABCWindow):
    __slots__ = ()

    def __init__(self, *widgets: Widget):
        super().__init__(*widgets)

