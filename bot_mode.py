from typing import Any
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from window import Window


class BotMode:
    __slots__ = ('name', 'values', 'has_custom_handler')

    # Вы можете использовать свой хендлер с фильтром IsModeName(name=mode_name)
    # или использовать системный хендлер по умолчанию
    # has_custom_handler блокирует обработку системного хендлера

    def __init__(self, name: str, values: list[str], has_custom_handler: bool = False):
        self.name = name
        self.values = values
        self.has_custom_handler = has_custom_handler


class ReplyBotMode(BotMode):
    __slots__ = ('name', 'values', 'alert_window', 'has_custom_handler')

    # alert_window используется для ReplyMode

    def __init__(self, name: str, values: list[str], alert_window: Window = None, has_custom_handler: bool = False):
        if (alert_window is None) and (not has_custom_handler):
            raise ValueError('alert_window must be defined if has_custom_handler is False')

        super().__init__(name=name, values=values, has_custom_handler=has_custom_handler)
        self.alert_window = alert_window


class BotModes:
    __slots__ = ('dict_modes', 'dict_values', 'fsm')

    def __init__(self, *modes: BotMode | ReplyBotMode, fsm: FSMContext = None) -> None:
        self.dict_modes = {}
        self.dict_values = {}
        self.fsm = fsm

        for mode in modes:
            self.dict_modes[mode.name] = mode
            self.dict_values[mode.name] = mode.values

    async def __sync_modes(self, fsm_data: dict[str, Any]):
        # Если модов нет в fsm, то записываем их из self.bot.modes
        if "__modes__" not in fsm_data:
            fsm_data["__modes__"] = self.dict_values
            await self.fsm.set_data(fsm_data)

    async def update_mode(self, name: str = None, event: Message | CallbackQuery = None) -> str:
        assert (name is not None) or (event is not None), ValueError("Name or Event required")
        assert self.dict_modes, ValueError("First set modes for Bot")
        # Если не задано имя режима, то извлекаем его из callback_data
        if name is None:
            # В CallbackButtonMode это значение после __mode:
            if isinstance(event, CallbackQuery):
                name = event.data.split(":")[1]
            # В ReplyButtonMode это значение ищем из списков существующих и мапим по имени:
            else:
                mode_state = [name for name, values in self.dict_values.items() if event.text in values]
                name = mode_state[0] if len(mode_state) > 0 else ""

        assert self.dict_values[name], ValueError("Bot don't have this mode")
        fsm_data = await self.fsm.get_data()
        # Если режимы уже есть в fsm, переносим активный в конец списка
        if "__modes__" in fsm_data.keys():
            last_active_mode = fsm_data["__modes__"][name].pop(0)
            fsm_data["__modes__"][name].append(last_active_mode)
        # Если режимы не заданы, берем их из бота
        else:
            fsm_data["__modes__"] = {name: self.dict_values["name"]}
        # Записываем данные с новым режимом
        await self.fsm.set_data(fsm_data)
        return name

    async def get_actual_modes(self) -> dict[str, list[str]]:
        fsm_data = await self.fsm.get_data()
        await self.__sync_modes(fsm_data=fsm_data)
        return fsm_data["__modes__"]

    async def get_mode_active_value(self, name: str) -> None:
        assert self.dict_values[name], ValueError("Bot don't have this mode")
        fsm_data = await self.fsm.get_data()
        await self.__sync_modes(fsm_data=fsm_data)
        # Активным считается первое значение режима
        return fsm_data["__modes__"][name][0]

