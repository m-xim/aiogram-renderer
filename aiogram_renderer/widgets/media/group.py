from typing import Any, List

from aiogram.types import InputMediaPhoto

from aiogram_renderer.types.data import RendererData
from aiogram_renderer.widgets import Widget
from aiogram_renderer.widgets.media.media import Media


class MediaGroup(Widget):
    __slots__ = ("medias",)

    # Укажите caption в файлах если хотите видеть в MediaGroup под каждым фото описание
    # По умолчанию, если у первого не указан caption он приравнивается тексту окна
    def __init__(self, *medias: Media, show_on: str = None):
        super().__init__(show_on=show_on)
        self.medias = medias

    async def _render(self, data: dict[str, Any], rdata: RendererData, **kwargs) -> list[Any]:
        """
        Метод сборки медиа группы
        :return:
        """
        build_medias: List[InputMediaPhoto] = []
        for media in self.medias:
            build_medias.append(await media.render(data=data, rdata=rdata, **kwargs))
        return build_medias
