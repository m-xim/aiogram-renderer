from abc import ABC, abstractmethod


class Widget(ABC):
    __slots__ = ("show_on",)

    def __init__(self, show_on: str = None):
        self.show_on = show_on

    @abstractmethod
    async def assemble(self, *args, **kwargs):
        pass
