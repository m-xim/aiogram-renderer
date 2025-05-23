from abc import ABC, abstractmethod


class Widget(ABC):
    __slots__ = ("when",)

    def __init__(self, when: str = None):
        self.when = when

    @abstractmethod
    async def assemble(self, *args, **kwargs):
        pass
