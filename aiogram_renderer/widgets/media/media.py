from typing import Any, Union, Literal
from aiogram.enums import ContentType
from aiogram.types import FSInputFile, InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument
from textcompose.core import Component

from aiogram_renderer.widgets import Widget
from pathlib import Path


class Media(Widget):
    # Укажите caption если хотите видеть в MediaGroup под каждым фото описание
    def __init__(
        self,
        path: str | Path,
        media_type: Literal[ContentType.PHOTO, ContentType.VIDEO, ContentType.AUDIO, ContentType.DOCUMENT],
        caption: str = None,
        show_on: str = None,
    ):
        """
        Виджет для отправки медиафайлов.

        :param path: Путь к файлу (строка или объект Path).
        :param media_type: Тип медиафайла (PHOTO, VIDEO, AUDIO, DOCUMENT).
        :param caption: Описание файла, отображаемое под медиа (опционально, для MediaGroup).
        :param show_on: Условие отображения виджета (опционально).
        """
        super().__init__(show_on=show_on)
        self.path = path
        self.caption = caption
        self.media_type = media_type

    async def _render(
        self, data: dict[str, Any], **kwargs
    ) -> Union[InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument]:
        caption_text = await self.resolve_value(self.caption, data)
        path_value = (
            FSInputFile(path=await self.resolve_value(self.path, data))
            if isinstance(self.path, str | Component)
            else self.path
        )
        # TODO: add support for URLInputFile and BufferedInputFile

        if self.media_type == ContentType.PHOTO:
            return InputMediaPhoto(media=path_value, caption=caption_text if caption_text else None)
        elif self.media_type == ContentType.VIDEO:
            return InputMediaVideo(
                media=path_value, caption=caption_text if caption_text else None, supports_streaming=True
            )
        elif self.media_type == ContentType.AUDIO:
            return InputMediaAudio(media=path_value, caption=caption_text if caption_text else None)
        else:
            return InputMediaDocument(media=path_value, caption=caption_text if caption_text else None)
