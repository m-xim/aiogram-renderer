from aiogram import Dispatcher
from aiogram_renderer.core.handlers.reply_router import router as reply_handlers
from aiogram_renderer.core.handlers.inline_router import router as inline_handlers
from .bot_mode import BotMode
from aiogram_renderer.core.middlewares import RendererMiddleware
from aiogram_renderer.windows.window import Window


async def configure_renderer(dp: Dispatcher, windows: list[Window] = None, modes: list[BotMode] = None) -> None:
    """
    Функция для конфигурации рендерера, для правильной работы задайте все Window, используемые в боте
    :param dp: telegram BOT Dispatcher
    :param windows: окна Window
    :param modes: режимы бота
    """
    # Подключаем системные хендлеры
    dp.include_routers(reply_handlers, inline_handlers)
    # Подключаем middleware, чтобы видеть объект renderer
    dp.update.middleware(RendererMiddleware(modes=modes, windows=windows))
