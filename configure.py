from aiogram import Dispatcher
from handlers.reply import router as reply_handler
from handlers.inline import router as inline_router
from bot_mode import BotMode
from middlewares import RendererMiddleware
from window import Window


async def configure_renderer(dp: Dispatcher, windows: list[Window] = None, modes: list[BotMode] = None) -> None:
    # Подключаем системные хендлеры
    dp.include_routers(reply_handler, inline_router)
    # Подключаем middleware, чтобы видеть объект renderer
    dp.update.middleware(RendererMiddleware(modes=modes, windows=windows))
