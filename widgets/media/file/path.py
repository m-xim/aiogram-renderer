from aiogram.types import FSInputFile
from widgets.text import Text
from widgets.widget import Widget


class File(Widget):
    __slots__ = ("file_name", "path", "media_caption")

    # Укажите caption если хотите видеть в MediaGroup под каждым фото описание
    # В случае отправки File отдельно используйте виджеты Text
    def __init__(self, file_name: str, path: str, media_caption: str | Text = None, when: str = None):
        super().__init__(when=when)

        self.file_name = file_name
        self.path = path
        self.media_caption = media_caption.content if isinstance(media_caption, Text) else media_caption

    def build(self, *args, **kwargs) -> FSInputFile:
        return FSInputFile(path=self.path, filename=self.file_name)

    async def format_key(self, key: str, value: str):
        """
        Форматирование filename, path, media_caption файла, по ключу из fsm
        :param key: ключ из window_data
        :param value: значение по ключу
        """

        # Подставляем значения в имя файла
        if '{' + key + '}' in self.file_name:
            self.file_name = self.file_name.replace('{' + key + '}', str(value))
        # Подставляем значения в путь файла
        if '{' + key + '}' in self.path:
            self.path = self.path.replace('{' + key + '}', str(value))
        # Подставляем значения в описание файла
        if self.media_caption is not None:
            if '{' + key + '}' in self.media_caption:
                self.media_caption = self.media_caption.replace('{' + key + '}', str(value))

    async def assemble(self, *args, **kwargs) -> FSInputFile:
        return FSInputFile(path=self.path, filename=self.file_name)


class Video(File):
    __slots__ = ()

    def __init__(self, file_name: str, path: str, media_caption: str | Text = None, when: str = None):
        super().__init__(file_name=file_name, path=path, media_caption=media_caption, when=when)


class Photo(File):
    __slots__ = ()

    def __init__(self, file_name: str, path: str, media_caption: str | Text = None, when: str = None):
        super().__init__(file_name=file_name, path=path, media_caption=media_caption, when=when)


class Audio(File):
    __slots__ = ()

    def __init__(self, file_name: str, path: str, media_caption: str | Text = None, when: str = None):
        super().__init__(file_name=file_name, path=path, media_caption=media_caption, when=when)
