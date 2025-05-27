from typing import Any
from aiogram import Bot
from aiogram.client.default import Default
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from pydantic_core import ValidationError
from bot_mode import BotModes
from enums import RenderMode
from widgets.keyboard.inline.panel import DynamicPanel
from widgets.media.file.bytes import FileBytes, AudioBytes, VideoBytes, PhotoBytes
from widgets.media.file.path import File, Audio, Video, Photo
from window import Window, Alert


class Renderer:
    __slots__ = ('bot', 'windows', 'fsm', 'bot_modes')

    def __init__(self, bot: Bot, windows: list[Window], fsm: FSMContext = None, bot_modes: BotModes = None):
        self.bot = bot
        self.windows = windows
        self.fsm = fsm
        self.bot_modes = bot_modes

    async def __sync_modes(self, fsm_data: dict[str, Any]) -> dict[str, Any]:
        """
        Метод для синхронизации режимов бота, все режимы проверяются на валидность
        :param fsm_data: FSM данные пользователя
        :return:
        """
        # Синхронизируем режимы (если режимы в боте не указаны мы убираем их из fsm)
        if (self.bot_modes is None) and ("__modes__" in fsm_data):
            fsm_data.pop("__modes__")
        elif (self.bot_modes is None) and ("__modes__" not in fsm_data):
            pass
        # В другом случае синхронизируем их
        else:
            fsm_data = await self.bot_modes.sync_modes(fsm_data)
        return fsm_data

    @staticmethod
    async def __sync_dpanels(fsm_data: dict[str, Any], data: dict[str, Any], window: Window) -> Any:
        """
        Метод для синхронизации данных динамических групп виджетов DynamicPanel с данными,
        переданными в метод render
        :param fsm_data: FSM данные пользователя
        :param data: данные переданные в render
        :param window: объект Window
        :return:
        """
        # Синхронизируем данные DynamicPanel (создаем поле __dpanels__ и помещаем туда новые данные DynamicPanel)
        for widget in window._widgets:
            if isinstance(widget, DynamicPanel):
                if "__dpanels__" not in fsm_data.keys():
                    fsm_data["__dpanels__"] = {}
                if data is not None:
                    if widget.name in data.keys():
                        fsm_data["__dpanels__"][widget.name] = data[widget.name]
        return fsm_data

    async def __sync_data(self, window: Window, data: dict) -> tuple[Any, dict[str, Any]]:
        """
        Метод для синхронизации данных переданных в метод render и FSM данных пользователя,
        синхронизируются данные окна, режимы и другие данные для специальных виджетов
        :param window: объект Window
        :param data: данные переданные в renderer
        :return:
        """
        fsm_data = await self.fsm.get_data()

        # В стейтах бота данные окон хранятся в fsm, в следующем формате
        # Словарь со стейтами окон задается в порядке их открытия, в каждом из них содержатся данные окна
        # '__windows__': {'State.step1': {'btn_text': 'default'...}, 'State.step2': {'btn_text': 'default2'...}...}
        state = window._state.state

        # Если окна есть в fsm
        if "__windows__" in fsm_data.keys():
            # Если окно присутствует в fsm и есть data, то выполняем merge, заменяя и дополняя данные
            if (state in fsm_data["__windows__"]) and (data is not None):
                fsm_data["__windows__"][state] |= data
            # Если окна нет в fsm и есть data, то сохраняем окно с заданной data
            elif (state not in fsm_data["__windows__"]) and (data is not None):
                fsm_data["__windows__"][state] = data
            # Если окна нет в fsm и нет data, то сохраняем окно с пустым data
            elif (state not in fsm_data["__windows__"]) and (data is None):
                fsm_data["__windows__"][state] = {}

        # Если окна нет в fsm, то создаем словарь __windows__ и добавляем туда окно с данными
        else:
            fsm_data["__windows__"] = {state: data} if data is not None else {state: {}}

        window_data = fsm_data["__windows__"][state]

        # Синхронизируем режимы
        fsm_data = await self.__sync_modes(fsm_data)

        # Синхронизируем DynamicPanel виджеты
        fsm_data = await self.__sync_dpanels(fsm_data=fsm_data, data=data, window=window)

        # Перезаписываем fsm
        await self.fsm.set_data(fsm_data)

        return window_data, fsm_data

    async def __get_window_by_state(self, state: str) -> Window:
        """
        Функция для получения объекта окна по FSM State, окна задаются в configure_renderer
        :param state: FSM State
        :return:
        """
        for i, window in enumerate(self.windows, start=1):
            if window._state == state:
                return window
            assert i != len(self.windows), ValueError("Окно не за задано в конфигурации")

    async def _switch_dynamic_panel_page(self, name: str, page: int):
        """
        Метод для переключения страницы группы - виджета DynamicPanel
        :param name: название группы, задается в виджете
        :param page: страница, на которую надо переключить
        """
        fsm_data = await self.fsm.get_data()
        # Устанавливаем новую активную страницу в группе
        fsm_data["__dpanels__"][name]["page"] = page
        await self.fsm.set_data(fsm_data)

    async def __render_media(self, file: File | FileBytes, data: dict[str, Any], text: str,
                             chat_id: int, message_id: int = None, mode: str = RenderMode.ANSWER,
                             reply_markup: Any = None, file_bytes: dict[str, bytes] = None) -> Message | None:
        """
        Метод рендеринга сообщения с медиа файлом
        :param file: виджет с файлом
        :param data: данные окна
        :param chat_id: id чата
        :param data: данные для передачи в окно
        :param message_id: id сообщения
        :param mode: режим рендеринга
        :param file_bytes: словарь с байтами файл(а|ов)
        :return:
        """
        # По умолчанию берем тот текст, что задан в виджетах окна, media_caption будет использоваться для
        # медиа групп
        file_obj, caption_text = await file.assemble(data=data, file_bytes=file_bytes)

        if mode == RenderMode.EDIT:
            try:
                await self.bot.edit_message_media(chat_id=chat_id, message_id=message_id,
                                                  reply_markup=reply_markup, media=file_obj)
            # Если нет медиафайла пропускаем ошибку
            except ValidationError:
                pass
            # Редактируем текст сообщения|caption
            finally:
                message = await self.bot.edit_message_caption(chat_id=chat_id,
                                                              message_id=message_id, reply_markup=reply_markup,
                                                              caption=text)
        else:
            # Если режим DELETE_AND_SEND - удаляем сообщение и убираем reply_to_message_id
            if mode == RenderMode.DELETE_AND_SEND:
                await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
                message_id = None

            # В режимах ANSWER, REPLY - отправляем сообщение с media
            if isinstance(file, (Photo, PhotoBytes)):
                message = await self.bot.send_photo(chat_id=chat_id, photo=file_obj, caption=text,
                                                    reply_to_message_id=message_id, reply_markup=reply_markup)
            elif isinstance(file, (Video, VideoBytes)):
                message = await self.bot.send_video(chat_id=chat_id, video=file_obj, caption=text,
                                                    supports_streaming=True, reply_to_message_id=message_id,
                                                    reply_markup=reply_markup)
            elif isinstance(file, (Audio, AudioBytes)):
                message = await self.bot.send_audio(chat_id=chat_id, audio=file_obj, caption=text,
                                                    reply_to_message_id=message_id, reply_markup=reply_markup)
            else:
                message = await self.bot.send_document(chat_id=chat_id, document=file_obj, caption=text,
                                                       reply_to_message_id=message_id,
                                                       reply_markup=reply_markup)
        return message

    async def render(self, window: str | Alert | Window, chat_id: int, data: dict[str, Any] = None,
                     message_id: int = None,
                     mode: str = RenderMode.ANSWER,
                     parse_mode: str = Default("parse_mode"),
                     file_bytes: dict[str, bytes] = None) -> tuple[Message | None, Window]:
        """
        Основной метод для преобразования окна в сообщение Telegram
        :param window: параметр State.state или объект Alert | Window
        :param chat_id: id чата
        :param data: данные для передачи в окно
        :param message_id: id сообщения
        :param mode: режим рендеринга
        :param parse_mode: режим парсинга
        :param file_bytes: словарь с байтами файл(а|ов)
        :return:
        """
        if message_id is None:
            assert mode != RenderMode.REPLY, ValueError("message_id is required on REPLY mode")
            assert mode != RenderMode.DELETE_AND_SEND, ValueError("message_id is required on mode DELETE_AND_SEND")

        if isinstance(window, Alert):
            fsm_data = await self.fsm.get_data()
            # Синхронизируем режимы
            fsm_data = await self.__sync_modes(fsm_data=fsm_data)
            await self.fsm.set_data(fsm_data)
            window_data = data if data is not None else {}
        else:
            # Если передали Window берем state из него
            if isinstance(window, Window):
                state = window._state
            else:
                state = window
                window = await self.__get_window_by_state(state=state)

            await self.fsm.set_state(state=state)

            # Синхронизируем данные окна
            window_data, fsm_data = await self.__sync_data(window=window, data=data)

        # Собираем и форматируем клавиатуру и текст
        modes = fsm_data["__modes__"] if "__modes__" in fsm_data else {}
        file, text, reply_markup = await window.assemble(data=window_data, modes=modes, dpanels=fsm_data["__dpanels__"])
        # Проверяем прикреплен ли файл к окну
        if file is not None:
            return await self.__render_media(file=file, data=window_data, text=text, reply_markup=reply_markup,
                                             chat_id=chat_id, message_id=message_id,
                                             mode=mode, file_bytes=file_bytes), window

        # Елси не прикреплен, выбираем тип отправки сообщения
        if mode == RenderMode.REPLY:
            message = await self.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup,
                                                  parse_mode=parse_mode, reply_to_message_id=message_id)

        elif mode == RenderMode.DELETE_AND_SEND:
            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
            message = await self.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup,
                                                  parse_mode=parse_mode)

        elif mode == RenderMode.EDIT:
            message = await self.bot.edit_message_text(chat_id=chat_id, text=text, message_id=message_id,
                                                       reply_markup=reply_markup, parse_mode=parse_mode)

        # RenderMode.ANSWER в других случаях
        else:
            message = await self.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup,
                                                  parse_mode=parse_mode)

        return message, window

    async def answer(self, window: str | Alert | Window, chat_id: int, data: dict[str, Any] = None,
                     parse_mode: ParseMode = Default("parse_mode"),
                     file_bytes: dict[str, bytes] = None) -> tuple[Message, Window]:
        return await self.render(window=window, chat_id=chat_id, parse_mode=parse_mode, mode=RenderMode.ANSWER,
                                 data=data, file_bytes=file_bytes)

    async def edit(self, window: str | Alert | Window, chat_id: int, message_id: int, data: dict[str, Any] = None,
                   parse_mode: ParseMode = Default("parse_mode"),
                   file_bytes: dict[str, bytes] = None) -> tuple[Message, Window]:
        return await self.render(window=window, chat_id=chat_id, message_id=message_id, parse_mode=parse_mode,
                                 mode=RenderMode.EDIT, data=data, file_bytes=file_bytes)

    async def delete_and_send(self, window: str | Alert | Window, chat_id: int, message_id: int,
                              data: dict[str, Any] = None, parse_mode: ParseMode = Default("parse_mode"),
                              file_bytes: dict[str, bytes] = None) -> tuple[Message, Window]:
        return await self.render(window=window, chat_id=chat_id, message_id=message_id, parse_mode=parse_mode,
                                 mode=RenderMode.DELETE_AND_SEND, data=data, file_bytes=file_bytes)

    async def reply(self, window: str | Alert | Window, chat_id: int, message_id: int, data: dict[str, Any] = None,
                    parse_mode: ParseMode = Default("parse_mode"),
                    file_bytes: dict[str, bytes] = None) -> tuple[Message, Window]:
        return await self.render(window=window, chat_id=chat_id, message_id=message_id, parse_mode=parse_mode,
                                 mode=RenderMode.REPLY, data=data, file_bytes=file_bytes)
