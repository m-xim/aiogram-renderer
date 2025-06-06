from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from aiogram_renderer.core.callback_data import ModeCD
from .renderer import Renderer


class IsModeWithNotCustomHandler(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, renderer: Renderer) -> bool:
        bot_mode_manager = renderer.bot_mode_manager
        if not bot_mode_manager:
            return False

        mode = None
        callback_data = None
        # Для CallbackQuery проверяем правильно ли задан callback_data по системному префиксу
        if isinstance(event, CallbackQuery):
            try:
                callback_data = ModeCD.unpack(event.data)
                if callback_data:
                    mode = await bot_mode_manager.find_by_name(name=callback_data.name)
            except (TypeError, ValueError):
                pass
        elif isinstance(event, Message):
            modes_values = await bot_mode_manager.all_values()
            if event.text in modes_values:
                mode = await bot_mode_manager.find_by_value(value=event.text)

        if mode and not mode.has_custom_handler:
            if callback_data:
                return {"callback_data": callback_data}
            return True
        return False


class IsMode(BaseFilter):
    def __init__(self, name: str):
        self.name = name

    async def __call__(self, event: Message | CallbackQuery, renderer: Renderer) -> bool:
        bot_mode_manager = renderer.bot_mode_manager
        if not bot_mode_manager:
            return False

        if self.name not in bot_mode_manager.modes:
            raise ValueError("Такого режима нет")

        mode = await bot_mode_manager.find_by_name(name=self.name)
        if not mode:
            return False

        if isinstance(event, CallbackQuery):
            # Проверяем равен ли callback заданному режиму
            callback_data = ModeCD(name=self.name)
            if event.data == callback_data.pack():
                return {"callback_data": callback_data}
        elif isinstance(event, Message):
            # Проверяем есть ли значение Reply text в values режима
            return event.text in mode.values

        return False
