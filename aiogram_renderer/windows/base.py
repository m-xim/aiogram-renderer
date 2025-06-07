from abc import ABC
from typing import Any, Union, Dict, List, Optional
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from textcompose import Template
from textcompose.core import Component

from aiogram_renderer.types.data import RendererData
from aiogram_renderer.widgets import Widget
from aiogram_renderer.widgets.keyboard.inline import InlineButton, InlinePanel, DynamicPanel
from aiogram_renderer.widgets.keyboard.reply import ReplyButton, ReplyPanel
from aiogram_renderer.widgets.media.media import Media


class BaseWindow(ABC):
    __slots__ = ("_widgets",)

    def __init__(self, *widgets: Union[Widget, Component]):
        """
        Основной класс окна, может быть 2 типов: Alert (не хранит в памяти данные окон) и
        Window (данные хранятся в памяти)
        :param widgets: виджеты
        """
        self._widgets = list(widgets)

    async def render_keyboard(
        self, data: dict[str, Any], rdata: RendererData
    ) -> Optional[Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]]:
        """
        Генерирует клавиатуру для окна на основе виджетов.
        :param data: данные окна
        :param rdata: вспомогательные данные рендера
        :return: ReplyMarkup или None, если кнопок нет
        """
        keyboard: List[List[Any]] = []
        button_objs: List[Widget] = []
        has_panel = False
        is_inline = False

        # Сначала собираем подходящие виджеты и определяем тип клавиатуры
        for widget in self._widgets:
            if isinstance(widget, (InlineButton, InlinePanel, DynamicPanel, ReplyButton, ReplyPanel)):
                button_objs.append(widget)
                if isinstance(widget, (InlinePanel, ReplyPanel, DynamicPanel)):
                    has_panel = True
                if isinstance(widget, (InlineButton, InlinePanel, DynamicPanel)):
                    is_inline = True

        if not button_objs:
            return None

        if has_panel:
            for b in button_objs:
                btn_object = await b.render(data=data, rdata=rdata)
                if btn_object is not None:
                    if isinstance(b, (InlinePanel, ReplyPanel, DynamicPanel)):
                        keyboard.extend(btn_object)
                    else:
                        keyboard.append([btn_object])
        else:
            row = []
            for b in button_objs:
                button_obj = await b.render(data=data, rdata=rdata)
                if button_obj is not None:
                    row.append(button_obj)
            if row:
                keyboard.append(row)

        if not keyboard:
            return None

        if is_inline:
            return InlineKeyboardMarkup(inline_keyboard=keyboard)
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    async def render_text(self, data: dict[str, Any], rdata: RendererData) -> str:
        """
        Генерирует текст из Template-виджетов.
        :param data: данные окна
        :return: текст
        """
        texts = []
        for widget in self._widgets:
            if isinstance(widget, Template):
                texts.append(widget.render(context=data, rdata=rdata))
        return "\n".join(texts)

    async def render_media(self) -> Optional[Media]:
        """
        Метод для получения медиа
        :return:
        """
        for widget in self._widgets:
            if isinstance(widget, Media):
                return widget
        return None

    async def render(
        self, wdata: Dict[str, Any], rdata: RendererData
    ) -> tuple[Optional[Media], str, Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]]:
        reply_markup = await self.render_keyboard(data=wdata, rdata=rdata)
        text = await self.render_text(data=wdata, rdata=rdata)
        file = await self.render_media()
        return file, text, reply_markup
