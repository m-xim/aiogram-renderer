from abc import ABC
from typing import Any, Union, Dict
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from textcompose import Template
from textcompose.core import Component

from aiogram_renderer.types.data import RendererData
from aiogram_renderer.widgets import Widget
from aiogram_renderer.widgets.keyboard.inline import InlineButton, InlinePanel, DynamicPanel
from aiogram_renderer.widgets.keyboard.reply import ReplyButton, ReplyPanel
from aiogram_renderer.widgets.media.media import Media


class BaseWindow(ABC):
    __slots__ = ("_widgets", "_state")

    def __init__(self, *widgets: Union[Widget | Component]):
        """
        Основной класс окна, может быть 2 типов: Alert (не хранит в памяти данные окон) и
        Window (данные хранятся в памяти)
        :param widgets: виджеты
        """
        self._widgets = list(widgets)

    async def render_keyboard(self, data: dict[str, Any], rdata: RendererData) -> Any:
        """
        Генерирует клавиатуру для окна на основе виджетов.
        Кнопки и панели добавляются в зависимости от условий видимости и наличия данных.
        :param data: данные окна
        :param rdata: вспомогательные данные рендера
        :return: ReplyMarkup или None, если кнопок нет
        """
        keyboard = []
        button_objs = []
        has_groups = False
        is_inline_keyboard = False

        # Сначала собираем подходящие виджеты и определяем тип клавиатуры
        for widget in self._widgets:
            if isinstance(widget, (InlineButton, InlinePanel, DynamicPanel, ReplyButton, ReplyPanel)):
                if isinstance(widget, (InlinePanel, ReplyPanel, DynamicPanel)):
                    has_groups = True
                if isinstance(widget, (InlineButton, InlinePanel, DynamicPanel)):
                    is_inline_keyboard = True
                button_objs.append(widget)

        if has_groups:
            # Если есть панели, добавляем их строки по одной
            for b in button_objs:
                btn_object = await b.render(data=data, rdata=rdata)
                if btn_object is not None:
                    if isinstance(b, (InlinePanel, ReplyPanel, DynamicPanel)):
                        keyboard.extend(btn_object)  # Добавляем строки панели
                    else:
                        keyboard.append([btn_object])  # Обычная кнопка — новая строка
        elif button_objs:
            # Если только кнопки, все в одной строке
            row = []
            for b in button_objs:
                button_obj = await b.render(data=data, rdata=rdata)
                if button_obj is not None:
                    row.append(button_obj)
            if row:
                keyboard.append(row)
        else:
            return None  # Нет ни кнопок, ни панелей

        # Возвращаем соответствующий markup
        if is_inline_keyboard:
            return InlineKeyboardMarkup(inline_keyboard=keyboard)
        else:
            return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    async def render_text(self, data: dict[str, Any], rdata: RendererData) -> str:
        """
        Метод для генерации текста, формируется общий текст из текстовых виджетов, также
        проводится проверка when фильтра на видимость и наличие ключей {key} в data
        :param data: данные окна
        :return:
        """
        text = ""
        for widget in self._widgets:
            if isinstance(widget, Template):
                text = widget.render(context=data, rdata=rdata)
                break
        return text

    async def render_media(self) -> Media | None:
        """
        Метод для получения файлового объекта
        :return:
        """
        for widget in self._widgets:
            if isinstance(widget, Media):
                return widget
        return None

    async def render(self, wdata: Dict[str, Any], rdata: RendererData) -> tuple:
        reply_markup = await self.render_keyboard(data=wdata, rdata=rdata)
        text = await self.render_text(data=wdata, rdata=rdata)
        file = await self.render_media()
        return file, text, reply_markup
