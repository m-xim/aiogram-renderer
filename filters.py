from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from bot_mode import ReplyBotMode, BotMode
from renderer import Renderer
from widgets.keyboard.reply.button import ReplyMode


class HasBotModes(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, renderer: Renderer) -> bool:
        # Проверяем заданы ли режимы
        return renderer.bot_modes is not None


class HasNotCustomHandler(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, renderer: Renderer) -> bool:
        # Проверяем правильно ли задан callback_data по системному префиксу
        if isinstance(event, CallbackQuery):
            if event.data[:9] != "__mode__:":
                return False
            # Для колбека берем название мода, указанное после "__mode:"
            mode_name = event.data[9:]
            # Проверяем нет ли у данного режима своего хендлера
            return not renderer.bot_modes.dict_modes[mode_name].has_custom_handler

        # Для сообщения, ищем его среди списков значений модов и выводим по найденному названию мода
        else:
            for name, values in renderer.bot_modes.dict_values.items():
                if event.text in values:
                    # Проверяем нет ли у данного режима своего хендлера
                    return not renderer.bot_modes.dict_modes[name].has_custom_handler

        return False


class IsUpdateModeMessage(BaseFilter):
    async def __call__(self, message: Message, renderer: Renderer) -> bool:
        for name, mode in renderer.bot_modes.dict_modes.items():
            # Является ли сообщение режимом reply и есть ли оно в его значениях
            if isinstance(mode, ReplyBotMode) and (message.text in mode.values):
                return True
        return False


class IsModeName(BaseFilter):
    def __init__(self, name: str):
        self.name = name

    async def __call__(self, event: Message | CallbackQuery, renderer: Renderer) -> bool:
        # Проверяем заданы ли режимы и есть ли такой режим
        if (renderer.bot_modes is not None) and (self.name in renderer.bot_modes.dict_modes):
            mode = renderer.bot_modes.dict_modes[self.name]
            # Проверяем равен ли коллбек заданному режиму
            if isinstance(event, CallbackQuery) and isinstance(mode, BotMode):
                return True if event.data == "__mode__:" + self.name else False
            # Проверяем есть ли значение Reply text в values режима
            elif isinstance(event, Message) and isinstance(mode, ReplyMode):
                return event.text in sum(renderer.bot_modes.dict_values[self.name].values(), [])
            else:
                return False
        else:
            return False
