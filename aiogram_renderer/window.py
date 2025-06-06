from abc import ABC
from aiogram.fsm.state import State
from typing import Any, Union, Dict
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from textcompose import Template
from textcompose.core import Component

from .types.data import RendererData
from .widgets.keyboard.inline import InlineButton, Mode, InlinePanel, DynamicPanel
from .widgets.media import File, FileBytes
from .widgets.keyboard.reply import ReplyButton, ReplyPanel
from .widgets import Widget
from .widgets.media.media import Media


class ABCWindow(ABC):
    __slots__ = ("_widgets", "_state")

    def __init__(self, *widgets: Union[Widget | Component]):
        """
        Основной класс окна, может быть 2 типов: Alert (не хранит в памяти данные окон) и
        Window (данные хранятся в памяти)
        :param widgets: виджеты
        """
        self._widgets = list(widgets)

    async def gen_reply_markup(self, data: dict[str, Any], modes: dict[str, Any], dpanels: dict[str, Any]) -> Any:
        """
        Метод для генерации клавиатуры, формируются кнопки, ReplyMarkup, а также внутри самих виджетов
        проводится проверка when фильтра на видимость и наличие ключей {key} в data
        :param data: данные окна
        :param modes: режимы FSM
        :param dpanels: динамические группы FSM (DynamicPanel виджет)
        :return:
        """
        keyboard = []
        button_objs = []
        has_groups = False
        is_inline_keyboard = False

        for widget in self._widgets:
            if isinstance(widget, (InlineButton, InlinePanel, DynamicPanel, ReplyButton, ReplyPanel)):
                if isinstance(widget, (InlinePanel, ReplyPanel, DynamicPanel)):
                    has_groups = True
                if isinstance(widget, (InlineButton, InlinePanel, DynamicPanel)):
                    is_inline_keyboard = True

                button_objs.append(widget)

        # Если есть виджет Panel, то добавляем его строки в клавиатуру
        if has_groups:
            for b in button_objs:
                btn_object = await b.render(data=data, modes=modes, dpanels=dpanels)
                # Если после сборки не None (тоесть кнопка видна, то добавляем ее в клавиатуру)
                if btn_object is not None:
                    # Если Panel, то добавляем его строки в клавиатуру
                    if isinstance(b, (InlinePanel, ReplyPanel, DynamicPanel)):
                        for button_row in btn_object:
                            keyboard.append(button_row)
                    else:  # Иначе, если Button, то добавляем его в новую строку
                        keyboard.append([btn_object])

        # Если Panel нет, то все кнопки устанавливаются в одной строке
        elif button_objs:
            keyboard.append([])
            for b in button_objs:
                button_obj = await b.render(data=data, modes=modes, dpanels=dpanels)
                # Если после сборки не None (тоесть кнопка видна, то добавляем ее в клавиатуру)
                if button_obj is not None:
                    keyboard[0].append(button_obj)

        # Если Panel нет и кнопок нет, то возвращаем None
        else:
            return None

        # Если есть клавиатура, задаем ReplyMarkup
        if is_inline_keyboard:
            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        else:
            reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

        return reply_markup

    async def gen_text(self, data: dict[str, Any]) -> str:
        """
        Метод для генерации текста, формируется общий текст из текстовых виджетов, также
        проводится проверка when фильтра на видимость и наличие ключей {key} в data
        :param data: данные окна
        :return:
        """
        text = ""
        for widget in self._widgets:
            if isinstance(widget, Template):
                text = widget.render(context=data)
        return text

    async def get_media(self) -> File | FileBytes | None:
        """
        Метод для получения файлового объекта
        :return:
        """
        for widget in self._widgets:
            if isinstance(widget, Media):
                return widget
        return None

    async def render(self, wdata: Dict[str, Any], rdata: RendererData) -> tuple:
        reply_markup = await self.gen_reply_markup(data=wdata, modes=rdata.modes, dpanels=rdata.dpanels)
        text = await self.gen_text(data=wdata)
        file = await self.get_media()
        return file, text, reply_markup


class Window(ABCWindow):
    __slots__ = ("_state",)

    def __init__(self, *widgets: Union[Widget | Component], state: State):
        self._state = state
        super().__init__(*widgets)


class Alert(ABCWindow):
    __slots__ = ()

    def __init__(self, *widgets: Union[Widget | Component]):
        for widget in widgets:
            if isinstance(widget, DynamicPanel):
                raise ValueError("Alert не поддерживает DynamicPanel (пока)")
            if isinstance(widget, Mode):
                raise ValueError("Alert не поддерживает Mode (пока)")
        super().__init__(*widgets)
