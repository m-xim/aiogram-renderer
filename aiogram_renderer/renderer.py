from typing import Any
from aiogram import Bot
from aiogram.client.default import Default
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from .bot_mode import BotModes
from .enums import RenderMode
from .types.data import RendererData
from .window import Window, Alert


class Renderer:
    def __init__(self, bot: Bot, windows: list[Window], fsm: FSMContext = None, bot_modes: BotModes = None):
        self.bot = bot
        self.windows = windows
        self.fsm: FSMContext = fsm
        self.bot_modes = bot_modes
        self.progress_updates = {}

    async def renderer_data(self):
        data = (await self.fsm.get_data()).get("renderer_data")
        print(await self.fsm.get_data())
        if not data:
            return RendererData()
        return RendererData(**data)

    async def update_renderer_data(self, data: RendererData):
        await self.fsm.update_data(renderer_data=data.model_dump(mode="json", exclude_defaults=True))

    async def get_window_by_state(self, state: str) -> Window:
        """
        Функция для получения объекта окна по FSM State, окна задаются в configure_renderer
        :param state: FSM State
        :return:
        """
        for i, window in enumerate(self.windows, start=1):
            if window._state == state:
                return window
        else:
            # !!!возможно стоит заменить на None
            raise ValueError("Окно не за задано в конфигурации")

    async def render(
        self,
        window: str | Alert | Window,
        chat_id: int,
        data: dict[str, Any] = None,
        message_id: int = None,
        mode: str = RenderMode.ANSWER,
        parse_mode: str = Default("parse_mode"),
        file_bytes: dict[str, bytes] = None,
    ) -> tuple[Message | None, Window]:
        if message_id is None:
            if mode == RenderMode.REPLY:
                raise ValueError("message_id is required on REPLY mode")
            if mode == RenderMode.DELETE_AND_SEND:
                raise ValueError("message_id is required on mode DELETE_AND_SEND")

        rdata = await self.renderer_data()

        if isinstance(window, Alert):
            # TODO: Добавить fsm_data = await self.__sync_modes(fsm_data=fsm_data)

            wdata = data or {}
        else:
            # Если передали Window берем state из него
            if isinstance(window, Window):
                state = window._state
            else:
                state = window
                window = await self.get_window_by_state(state=state)

            await self.fsm.set_state(state=state)

            # Синхронизируем данные окна
            if data:
                rdata.windows[window._state.state] = data
                await self.update_renderer_data(rdata)
                rdata = await self.renderer_data()
                wdata = rdata.windows[window._state.state]
            else:
                wdata = None

        # Собираем и форматируем клавиатуру и текст
        file, text, reply_markup = await window.render(wdata=wdata, rdata=rdata)
        # Проверяем прикреплен ли файл к окну
        # if file is not None:
        #     return await self.__render_media(file=file, data=wdata, text=text, reply_markup=reply_markup,
        #                                      chat_id=chat_id, message_id=message_id,
        #                                      mode=mode, file_bytes=file_bytes), window

        # Еcли не прикреплен, выбираем тип отправки сообщения
        if mode == RenderMode.REPLY:
            message = await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
                reply_to_message_id=message_id,
            )

        elif mode == RenderMode.DELETE_AND_SEND:
            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
            message = await self.bot.send_message(
                chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode
            )

        elif mode == RenderMode.EDIT:
            message = await self.bot.edit_message_text(
                chat_id=chat_id, text=text, message_id=message_id, reply_markup=reply_markup, parse_mode=parse_mode
            )

        # RenderMode.ANSWER в других случаях
        else:
            message = await self.bot.send_message(
                chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode
            )

        return message, window

    async def answer(
        self,
        window: str | Alert | Window,
        chat_id: int,
        data: dict[str, Any] = None,
        parse_mode: ParseMode = Default("parse_mode"),
        file_bytes: dict[str, bytes] = None,
    ) -> tuple[Message, Window]:
        return await self.render(
            window=window,
            chat_id=chat_id,
            parse_mode=parse_mode,
            mode=RenderMode.ANSWER,
            data=data,
            file_bytes=file_bytes,
        )

    async def edit(
        self,
        window: str | Alert | Window,
        chat_id: int,
        message_id: int,
        data: dict[str, Any] = None,
        parse_mode: ParseMode = Default("parse_mode"),
        file_bytes: dict[str, bytes] = None,
    ) -> tuple[Message, Window]:
        return await self.render(
            window=window,
            chat_id=chat_id,
            message_id=message_id,
            parse_mode=parse_mode,
            mode=RenderMode.EDIT,
            data=data,
            file_bytes=file_bytes,
        )

    async def delete_and_send(
        self,
        window: str | Alert | Window,
        chat_id: int,
        message_id: int,
        data: dict[str, Any] = None,
        parse_mode: ParseMode = Default("parse_mode"),
        file_bytes: dict[str, bytes] = None,
    ) -> tuple[Message, Window]:
        return await self.render(
            window=window,
            chat_id=chat_id,
            message_id=message_id,
            parse_mode=parse_mode,
            mode=RenderMode.DELETE_AND_SEND,
            data=data,
            file_bytes=file_bytes,
        )

    async def reply(
        self,
        window: str | Alert | Window,
        chat_id: int,
        message_id: int,
        data: dict[str, Any] = None,
        parse_mode: ParseMode = Default("parse_mode"),
        file_bytes: dict[str, bytes] = None,
    ) -> tuple[Message, Window]:
        return await self.render(
            window=window,
            chat_id=chat_id,
            message_id=message_id,
            parse_mode=parse_mode,
            mode=RenderMode.REPLY,
            data=data,
            file_bytes=file_bytes,
        )
