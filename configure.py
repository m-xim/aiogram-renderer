from aiogram import Dispatcher
from handlers.reply_router import router as reply_handlers
from handlers.inline_router import router as inline_handlers
from bot_mode import BotMode
from middlewares import RendererMiddleware
from window import Window


async def configure_renderer(dp: Dispatcher, windows: list[Window] = None, modes: list[BotMode] = None) -> None:
    # Подключаем системные хендлеры
    dp.include_routers(reply_handlers, inline_handlers)
    # Подключаем middleware, чтобы видеть объект renderer
    dp.update.middleware(RendererMiddleware(modes=modes, windows=windows))
