from typing import Any
from aiogram.types import FSInputFile
from aiogram_renderer.widgets import Widget
from pathlib import Path


class Media(Widget):
    # Укажите caption если хотите видеть в MediaGroup под каждым фото описание
    # В случае отправки File отдельно используйте виджеты Text или Multi
    def __init__(self, path: str | Path, type, caption: str = None, show_on: str = None):
        """
        Виджет с файлом
        :param photo: картинка
        :param caption: описание файла для MediaGroup
        :param show_on: фильтр видимости
        """
        super().__init__(show_on=show_on)
        self.path = path
        self.caption = caption
        self.type = type

    async def _render(self, data: dict[str, Any], **kwargs) -> tuple[FSInputFile | None, str]:
        caption_text = self.resolve_value(self.caption, data)
        path_text = self.resolve_value(self.path, data) if isinstance(self.path, str) else self.path

        return caption_text, path_text, self.type
