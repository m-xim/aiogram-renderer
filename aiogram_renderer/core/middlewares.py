from typing import Any, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from aiogram_renderer.bot_mode import BotMode
from aiogram_renderer.renderer import Renderer
from aiogram_renderer.windows.window import Window


class RendererMiddleware(BaseMiddleware):
    def __init__(self, windows: list[Window] = None, modes: list[BotMode] = None):
        self.windows = windows
        self.modes = modes

    async def __call__(self, handler: Callable, event: Message, data: Dict[str, Any]) -> Any:
        # Если есть FSMContext, то передаем его в renderer и bot_modes
        if (fsm := data.get("state")) is not None:
            data["renderer"] = Renderer(
                bot=event.bot,
                fsm=fsm,
                middleware_data=data,
                windows=self.windows,
                bot_modes=self.modes,
            )

        return await handler(event, data)
