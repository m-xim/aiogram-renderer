from aiogram import types
from aiogram import BaseMiddleware
from typing import Any, Callable
from aiogram.fsm.context import FSMContext
from bot_mode import BotModes, BotMode
from renderer import Renderer
from window import Window


class RendererMiddleware(BaseMiddleware):
    def __init__(self, windows: list[Window] = None, modes: list[BotMode] = None):
        self.windows = windows
        self.modes = modes

    async def __call__(self, handler: Callable, event: types.Message, data: dict[str, Any]) -> Any:
        renderer = Renderer(bot=event.bot, windows=self.windows, bot_modes=BotModes(*self.modes))
        # Если есть FSMContext т передаем его в renderer и bot_modes
        for key, value in data.items():
            if isinstance(value, FSMContext):
                renderer.fsm = value
                renderer.bot_modes.fsm = value
                break
        data["renderer"] = renderer
        result = await handler(event, data)
        del renderer
        return result
