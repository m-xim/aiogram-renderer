from typing import Any
from aiogram.types import BufferedInputFile
from widgets.text import Text, Area
from widgets.widget import Widget


class FileBytes(Widget):
    __slots__ = ("file_name", "bytes_name", "media_caption")

    # Укажите caption если хотите видеть в MediaGroup под каждым фото описание
    # В случае отправки File отдельно используйте виджеты Text, Multi
    def __init__(self, file_name: str, bytes_name: str, media_caption: str | Text = None, when: str = None):
        """
        Виджет для отправки байтов файла, так как не хранится в памяти - отобразить окно можно будет только один раз
        :param file_name: имя файла
        :param bytes_name: имя поля в file_bytes, где хранятся байты
        :param media_caption: описание файла для MediaGroup
        :param when: фильтр видимости
        """
        super().__init__(when=when)
        self.file_name = file_name
        self.bytes_name = bytes_name
        self.media_caption = media_caption

    async def assemble(self, data: dict[str, Any], **kwargs) -> tuple[BufferedInputFile, Any] | None:
        file_name = self.file_name

        if isinstance(self.media_caption, (Text, Area)):
            caption_text = await self.media_caption.assemble(data)
        else:
            caption_text = self.media_caption

        if self.when in data.keys():
            # Если when = False, не собираем кнопку и возвращаем None
            if not data[self.when]:
                return None

        # Форматируем по data, если там заданы ключи {key}
        for key, value in data.items():
            # Подставляем значения в имя файла
            if '{' + key + '}' in file_name:
                file_name = file_name.replace('{' + key + '}', str(value))
            # Подставляем значения в описание файла
            if isinstance(caption_text, str) and (caption_text != ""):
                if '{' + key + '}' in caption_text:
                    caption_text = caption_text.replace('{' + key + '}', str(value))

        return BufferedInputFile(file=kwargs["file_bytes"][self.bytes_name], filename=file_name), caption_text


class VideoBytes(FileBytes):
    __slots__ = ()

    def __init__(self, file_name: str, bytes_name: str, media_caption: str | Text = None, when: str = None):
        super().__init__(file_name=file_name, bytes_name=bytes_name,
                         media_caption=media_caption, when=when)


class PhotoBytes(FileBytes):
    __slots__ = ()

    def __init__(self, file_name: str, bytes_name: str, media_caption: str | Text = None, when: str = None):
        super().__init__(file_name=file_name, bytes_name=bytes_name,
                         media_caption=media_caption, when=when)


class AudioBytes(FileBytes):
    __slots__ = ()

    def __init__(self, file_name: str, bytes_name: str, media_caption: str | Text = None, when: str = None):
        super().__init__(file_name=file_name, bytes_name=bytes_name,
                         media_caption=media_caption, when=when)
