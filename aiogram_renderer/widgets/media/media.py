from urllib.parse import urlparse
from typing import Any, Union, Literal, Optional
from aiogram.enums import ContentType
from aiogram.types import (
    FSInputFile,
    URLInputFile,
    BufferedInputFile,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaAudio,
    InputMediaDocument,
)
from textcompose.core import Component
from aiogram_renderer.widgets import Widget
from pathlib import Path


class Media(Widget):
    def __init__(
        self,
        path: str | Path | FSInputFile | URLInputFile | BufferedInputFile | Component | bytes,
        media_type: Literal[ContentType.PHOTO, ContentType.VIDEO, ContentType.AUDIO, ContentType.DOCUMENT],
        caption: Optional[str] = None,
        filename: Optional[str] = None,
        show_on=None,
        **input_params: Any,
    ):
        """
        Виджет для отправки медиафайлов.

        :param path: Путь, URL, байты, компонент или InputFile.
        :param media_type: Тип медиафайла.
        :param caption: Описание файла (опционально).
        :param show_on: Условие отображения (опционально).
        """
        super().__init__(show_on=show_on)
        self.path = path
        self.caption = caption
        self.filename = filename
        self.media_type = media_type
        self.input_params = input_params

    async def _resolve_input_file(self, path, data) -> Union[FSInputFile, URLInputFile, BufferedInputFile]:
        value = await self.resolve_value(path, data)

        # Уже готовый InputFile
        if isinstance(value, (FSInputFile, URLInputFile, BufferedInputFile)):
            return value

        # Если байты - делаем буфер с дефолтным именем файла
        if isinstance(value, bytes):
            return BufferedInputFile(value, filename=self.filename or "file")

        # Если путь - Path или строка
        if isinstance(value, Path):
            return FSInputFile(path=str(value), filename=self.filename)
        if isinstance(value, str):
            if (parsed := urlparse(value)) in ("http", "https") and bool(parsed.netloc):
                return URLInputFile(value, filename=self.filename)
            else:
                return FSInputFile(path=value, filename=self.filename)

        raise ValueError(f"Не удалось определить тип файла для значения: {value!r}")

    async def _render(
        self, data: dict[str, Any], **kwargs
    ) -> Union[InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument]:
        caption_text = await self.resolve_value(self.caption, data)
        input_file = await self._resolve_input_file(self.path, data)

        if self.media_type == ContentType.PHOTO:
            return InputMediaPhoto(media=input_file, caption=caption_text or None, **self.input_params)
        elif self.media_type == ContentType.VIDEO:
            return InputMediaVideo(
                media=input_file, caption=caption_text or None, supports_streaming=True, **self.input_params
            )
        elif self.media_type == ContentType.AUDIO:
            return InputMediaAudio(media=input_file, caption=caption_text or None, **self.input_params)
        elif self.media_type == ContentType.DOCUMENT:
            return InputMediaDocument(media=input_file, caption=caption_text or None, **self.input_params)
        else:
            raise ValueError(f"Не поддерживаемый тип media_type: {self.media_type}")
