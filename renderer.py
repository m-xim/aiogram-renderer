from typing import Any
from aiogram import Bot
from aiogram.client.default import Default
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot_mode import BotModes
from enums import RenderMode
from window import Window, Alert


class Renderer:
    __slots__ = ('bot', 'windows', 'fsm', 'bot_modes',)

    def __init__(self, bot: Bot, windows: list[Window], fsm: FSMContext = None, bot_modes: BotModes = None):
        self.bot = bot
        self.windows = windows
        self.fsm = fsm
        self.bot_modes = bot_modes

    async def __sync_modes(self, fsm_data: dict[str, Any]) -> dict[str, Any]:
        # Синхронизируем режимы (если режимы в боте не указаны мы убираем их из fsm)
        if (self.bot_modes is None) and ("__modes__" in fsm_data):
            fsm_data.pop("__modes__")
        elif (self.bot_modes is None) and ("__modes__" not in fsm_data):
            pass
        # В другом случае синхронизируем их
        else:
            fsm_data = await self.bot_modes.sync_modes(fsm_data)
        return fsm_data

    async def __sync_data(self, window: Window, data: dict) -> tuple[Any, dict[str, Any]]:
        fsm_data = await self.fsm.get_data()

        # В стейтах бота данные окон хранятся в fsm, в следующем формате
        # Словарь со стейтами окон задается в порядке их открытия, в каждом из них содержатся данные окна
        # '__windows__': {'State.step1': {'btn_text': 'default'...}, 'State.step2': {'btn_text': 'default2'...}...}
        state = window.state.state

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
        # Перезаписываем fsm
        await self.fsm.set_data(fsm_data)

        return window_data, fsm_data

    async def __get_window_by_state(self, state: str) -> Window:
        for i, window in enumerate(self.windows, start=1):
            if window.state == state:
                return window
            assert i != len(self.windows), ValueError("This window didn't set in configure windows")

    async def switch_dynamic_group_page(self, name: str, page: int):
        fsm_data = await self.fsm.get_data()
        window_state = await self.fsm.get_state()
        # Устанавливаем новую активную страницу в группе
        fsm_data["__windows"][window_state][name]["page"] = page
        await self.fsm.set_data(fsm_data)

    async def render(self, window: str | Alert | Window, chat_id: int, data: dict[str, Any] = None, message_id: int = None,
                     mode: str = RenderMode.ANSWER, parse_mode: str = Default("parse_mode")) -> tuple[Message | None, Window]:
        """
        Основная функция для преобразования окна в сообщение Telegram
        :param window: параметр State.state объекта Window или Alert, Window
        :param chat_id: id чата
        :param data: данные для передачи в окно
        :param message_id: id сообщения
        :param mode: режим рендеринга
        :param parse_mode: режим парсинга
        :return:
        """
        if message_id is None:
            assert mode != RenderMode.REPLY, ValueError("message_id is required on REPLY mode")
            assert mode != RenderMode.DELETE_AND_SEND, ValueError("message_id is required on mode DELETE_AND_SEND")

        if isinstance(window, Alert):
            fsm_data = await self.fsm.get_data()
            fsm_data = await self.__sync_modes(fsm_data=fsm_data)
            await self.fsm.set_data(fsm_data)
            window_data = data if data is not None else {}
        else:
            # Если передали Window берем state из него
            if isinstance(window, Window):
                state = window.state
            else:
                state = window
                window = await self.__get_window_by_state(state=state)

            await self.fsm.set_state(state=state)

            # Синхронизируем данные окна
            window_data, fsm_data = await self.__sync_data(window=window, data=data)

        # Собираем и форматируем клавиатуру и текст
        modes = fsm_data["__modes__"] if "__modes__" in fsm_data else {}
        text, reply_markup = await window.assemble(data=window_data, modes=modes)

        # Выбор типа отправки сообщения
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
                     parse_mode: ParseMode = Default("parse_mode")) -> tuple[Message, Window]:
        return await self.render(window=window, chat_id=chat_id, parse_mode=parse_mode, mode=RenderMode.ANSWER,
                                 data=data)

    async def edit(self, window: str | Alert| Window, chat_id: int, message_id: int, data: dict[str, Any] = None,
                   parse_mode: ParseMode = Default("parse_mode")) -> tuple[Message, Window]:
        return await self.render(window=window, chat_id=chat_id, message_id=message_id, parse_mode=parse_mode,
                                 mode=RenderMode.EDIT, data=data)

    async def delete_and_send(self, window: str | Alert | Window, chat_id: int, message_id: int,
                              data: dict[str, Any] = None,
                              parse_mode: ParseMode = Default("parse_mode")) -> tuple[Message, Window]:
        return await self.render(window=window, chat_id=chat_id, message_id=message_id, parse_mode=parse_mode,
                                 mode=RenderMode.DELETE_AND_SEND, data=data)

    async def reply(self, window: str | Alert | Window, chat_id: int, message_id: int, data: dict[str, Any] = None,
                    parse_mode: ParseMode = Default("parse_mode")) -> tuple[Message, Window]:
        return await self.render(window=window, chat_id=chat_id, message_id=message_id, parse_mode=parse_mode,
                                 mode=RenderMode.REPLY, data=data)
