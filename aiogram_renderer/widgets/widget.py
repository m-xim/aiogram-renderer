from abc import ABC, abstractmethod
from typing import Mapping, Any, Callable

from magic_filter import MagicFilter
from textcompose.core import Component

from aiogram_renderer.types.data import RendererData

Condition = str | MagicFilter | Callable[[Mapping[str, Any]], bool] | Component | None
Value = str | MagicFilter | Callable[[Mapping[str, Any]], str | None] | Component | None


class Widget(ABC):
    __slots__ = (
        "data",
        "show_on",
    )

    def __init__(self, show_on: Condition = None):
        self.show_on = show_on

    @staticmethod
    async def resolve_value(value: Value, data: Mapping[str, Any]) -> str | None:
        if isinstance(value, Component):
            return value.render(context=data)
        if isinstance(value, MagicFilter):
            return value.resolve(data)
        if isinstance(value, Callable):
            return value(data)
        return value

    async def _check_show_on(self, data: Mapping[str, Any]) -> bool:
        if self.show_on is None:
            return True

        if isinstance(self.show_on, str):
            return bool(data.get(self.show_on))

        return bool(await self.resolve_value(value=self.show_on, data=data))

    async def render(self, data: Mapping[str, Any], rdata: RendererData, *args, **kwargs):
        if not await self._check_show_on(data):
            return None
        return await self._render(data, rdata=rdata, *args, **kwargs)

    @abstractmethod
    async def _render(self, data: Mapping[str, Any], rdata: RendererData, *args, **kwargs) -> str:
        raise NotImplementedError
