from typing import Optional, TYPE_CHECKING

from .types.bot_mode import BotMode


if TYPE_CHECKING:
    from .renderer import Renderer


class BotModeManager:
    """
    Управляет всеми режимами бота.
    """

    __slots__ = ("modes", "renderer")

    def __init__(self, *modes: BotMode, renderer: "Renderer") -> None:
        self.modes = list(modes)
        self.renderer = renderer

    def as_dict(self):
        return {mode.name: mode.values for mode in self.modes}

    async def all_values(self) -> list[str]:
        # Возвращает список всех значений всех режимов
        values = []
        for mode in self.modes:
            values.extend(mode.values)
        return values

    async def find_by_name(self, name: str) -> Optional[BotMode]:
        # Поиск режима по имени
        for mode in self.modes:
            if mode.name == name:
                return mode
        return None

    async def find_by_value(self, value: str) -> Optional[BotMode]:
        # Поиск режима по значению
        for mode in self.modes:
            if value in mode.values:
                return mode
        return None

    async def set_active_mode(self, mode_identifier: str) -> str:
        """
        Устанавливает активный режим по имени или значению.
        :param mode_identifier: имя режима или одно из его значений
        :return: имя активированного режима
        """
        rdata = await self.renderer.renderer_data()

        # Поиск по значению
        mode_name = None
        for name, values in rdata.modes.items():
            if mode_identifier in values:
                mode_name = name
                break
        # Поиск по имени
        if not mode_name and mode_identifier in rdata.modes:
            mode_name = mode_identifier
        if not mode_name:
            raise ValueError("У бота нет данного режима")

        # Переносим активный режим в конец списка
        last_active = rdata.modes[mode_name].pop(0)
        rdata.modes[mode_name].append(last_active)

        await self.renderer.update_renderer_data(rdata)

        return mode_name

    async def get_active_value(self, name: str) -> str:
        # Получить активное значение режима (первое в списке)
        modes = (await self.renderer.renderer_data()).modes
        if not modes.get(name):
            raise ValueError("У бота нет данного режима")
        return modes[name][0]
