from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from .callback_data import ModeCD
from .renderer import Renderer


class IsModeWithNotCustomHandler(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, renderer: Renderer) -> bool:
        # Если режимы заданы
        if renderer.bot_modes is not None:
            mode = None
            # Для CallbackQuery проверяем правильно ли задан callback_data по системному префиксу
            if isinstance(event, CallbackQuery):
                try:
                    callback_data = ModeCD.unpack(event.data)
                except (TypeError, ValueError):
                    callback_data = None

                if callback_data is not None:
                    # Проверяем нет ли у данного режима своего хендлера
                    mode = await renderer.bot_modes.get_mode_by_name(name=callback_data.name)

            # Для Message, ищем его среди списков значений модов и выводим по найденному названию мода
            else:
                modes_values = await renderer.bot_modes.get_modes_values()
                if event.text in modes_values:
                    # Проверяем нет ли у данного режима своего хендлера
                    mode = await renderer.bot_modes.get_mode_by_value(value=event.text)

            # Проверяем нашелся ли режим и есть ли у него пользовательский хендлер
            if (mode is not None) and (not mode.has_custom_handler):
                return True

        return False


class IsMode(BaseFilter):
    def __init__(self, name: str):
        self.name = name

    async def __call__(self, event: Message | CallbackQuery, renderer: Renderer) -> bool:
        # Проверяем заданы ли режимы и есть ли такой режим
        if renderer.bot_modes is not None:
            dict_modes = await renderer.bot_modes.get_dict_modes()
            if self.name in dict_modes.keys():
                mode = await renderer.bot_modes.get_mode_by_name(name=self.name)
                # Проверяем равен ли коллбек заданному режиму
                if isinstance(event, CallbackQuery):
                    if event.data == ModeCD(name=self.name).pack() and mode is not None:
                        return True
                # Проверяем есть ли значение Reply text в values режима
                elif isinstance(event, Message):
                    if event.text in mode.values and mode is not None:
                        return True
            else:
                raise ValueError("Такого режима нет")

        return False
