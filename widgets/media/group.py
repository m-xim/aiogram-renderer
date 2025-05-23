from typing import Any
from widgets.media.file.path import File, Video, Audio, Photo
from widgets.media.file.bytes import FileBytes, VideoBytes, AudioBytes, PhotoBytes
from aiogram.utils.media_group import MediaGroupBuilder
from widgets.widget import Widget


class MediaGroup(Widget):
    __slots__ = ("files",)

    # Укажите caption в файлах если хотите видеть в MediaGroup под каждым фото описание
    # По умолчанию, если у последнего файла не указан media_caption он приравнивается тексту окна
    def __init__(self, *files: File | FileBytes, when: str = None):
        super().__init__(when=when)

        self.files = list(files)

    async def build(self, window_text: str, files: dict[str, bytes] = None) -> list[Any]:
        """
        Метод сборки медиа группы телеграм
        :param window_text: отформатированный текст окна
        :param files: байты файлов, указать если есть
        :return:
        """
        # Собираем медиа группу
        media_group_builder = MediaGroupBuilder()

        # Если у последнего файла не указан media_caption он приравнивается тексту окна
        if self.files[-1].media_caption is None:
            self.files[-1].media_caption = window_text

        audio_or_documents = 0
        for f in self.files:
            f_obj = f.build(files)
            if isinstance(f, (Video, VideoBytes)):
                media_group_builder.add_video(media=f_obj, supports_streaming=True, caption=f.media_caption)
            elif isinstance(f, (Audio, AudioBytes)):
                audio_or_documents += 1
                media_group_builder.add_audio(media=f_obj, caption=f.media_caption)
            elif isinstance(f, (Photo, PhotoBytes)):
                media_group_builder.add_photo(media=f_obj, caption=f.media_caption)
            else:
                audio_or_documents += 1
                media_group_builder.add_document(media=f_obj, caption=f.media_caption)

        return media_group_builder.build()