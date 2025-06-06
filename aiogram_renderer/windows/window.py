from aiogram.fsm.state import State
from typing import Union
from textcompose.core import Component

from aiogram_renderer.widgets.keyboard.inline import Mode, DynamicPanel
from aiogram_renderer.widgets import Widget
from aiogram_renderer.windows.base import BaseWindow


class Window(BaseWindow):
    __slots__ = ("_state",)

    def __init__(self, *widgets: Union[Widget | Component], state: State):
        self._state = state
        super().__init__(*widgets)


class Alert(BaseWindow):
    __slots__ = ()

    def __init__(self, *widgets: Union[Widget | Component]):
        for widget in widgets:
            if isinstance(widget, DynamicPanel):
                raise ValueError("Alert не поддерживает DynamicPanel (пока)")
            if isinstance(widget, Mode):
                raise ValueError("Alert не поддерживает Mode (пока)")
        super().__init__(*widgets)
