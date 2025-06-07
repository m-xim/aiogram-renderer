from typing import Any, Callable, Dict, List

from aiogram import BaseMiddleware
from aiogram.types import Message


from aiogram_renderer.bot_mode import BotMode
from aiogram_renderer.renderer import Renderer
from aiogram_renderer.windows.window import Window


class RendererMiddleware(BaseMiddleware):
    def __init__(self, windows: List[Window] = None, modes: List[BotMode] = None):
        self.windows = windows
        self.modes = modes

    async def __call__(self, handler: Callable, event: Message, data: Dict[str, Any]) -> Any:
        fsm = data.get("state")
        if fsm is None:
            raise RuntimeError("FSMContext обязателен для работы Renderer. Проверьте, что в Dispatcher передан storage")
        data["renderer"] = Renderer(
            bot=event.bot,
            fsm=fsm,
            middleware_data=data,
            windows=self.windows,
            bot_modes=self.modes,
        )
        return await handler(event, data)
