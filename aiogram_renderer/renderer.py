from typing import Any, List, Dict, Union, Tuple, Optional
from aiogram import Bot
from aiogram.client.default import Default
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_renderer.types.enums import RenderMode
from .types.bot_mode import BotMode
from .types.data import RendererData
from .widgets.keyboard.inline import DynamicPanel
from aiogram_renderer.windows.window import Window, Alert
from aiogram_renderer.bot_mode import BotModeManager


class Renderer:
    def __init__(
        self,
        bot: Bot,
        windows: List[Window],
        middleware_data: Dict[str, Any],
        fsm: FSMContext,
        bot_modes: Optional[List[BotMode]] = None,
    ):
        self.bot = bot
        self.windows = windows
        self.middleware_data = middleware_data
        self.fsm = fsm
        self.bot_mode_manager = BotModeManager(*bot_modes, renderer=self) if bot_modes else None
        self.progress_updates = {}

    async def renderer_data(self) -> RendererData:
        data = (await self.fsm.get_data()).get("renderer_data")
        return RendererData(**data) if data else RendererData()

    async def update_renderer_data(self, data: RendererData):
        await self.fsm.update_data(renderer_data=data.model_dump(mode="json", exclude_defaults=True))

    async def get_window_by_state(self, state: str) -> Window:
        for window in self.windows:
            if window._state == state:
                return window
        raise ValueError("Окно не задано в конфигурации")

    async def _update_modes_and_panels(
        self, rdata: RendererData, window: Window, data: Optional[Dict[str, Any]]
    ) -> RendererData:
        if self.bot_mode_manager:
            rdata.modes = self.bot_mode_manager.as_dict()
        if data:
            for widget in window._widgets:
                if isinstance(widget, DynamicPanel) and widget.name in data:
                    rdata.dpanels[widget.name] = data[widget.name]
        await self.update_renderer_data(rdata)
        return await self.renderer_data()

    async def _send_message(
        self, mode: str, send_args: dict, chat_id: int, message_id: Optional[int] = None
    ) -> Optional[Message]:
        if mode == RenderMode.REPLY:
            send_args["reply_to_message_id"] = message_id
            return await self.bot.send_message(**send_args)
        elif mode == RenderMode.DELETE_AND_SEND:
            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
            return await self.bot.send_message(**send_args)
        elif mode == RenderMode.EDIT:
            return await self.bot.edit_message_text(
                chat_id=chat_id,
                text=send_args["text"],
                message_id=message_id,
                reply_markup=send_args.get("reply_markup"),
                parse_mode=send_args.get("parse_mode"),
            )
        else:
            return await self.bot.send_message(**send_args)

    async def render(
        self,
        window: Union[str, Alert, Window],
        chat_id: int,
        data: Optional[Dict[str, Any]] = None,
        message_id: Optional[int] = None,
        mode: str = RenderMode.ANSWER,
        parse_mode: str = Default("parse_mode"),
        file_bytes: Optional[Dict[str, bytes]] = None,
    ) -> Tuple[Optional[Message], Window]:
        if mode in {RenderMode.REPLY, RenderMode.DELETE_AND_SEND} and message_id is None:
            raise ValueError("message_id is required for REPLY and DELETE_AND_SEND modes")

        rdata = await self.renderer_data()

        wdata = data

        if not isinstance(window, Alert):
            if not isinstance(window, Window):
                window = await self.get_window_by_state(window)
            state = window._state
            await self.fsm.set_state(state)

            # Обновление данных окна
            if data:
                rdata.windows[state.state] = data
                await self.update_renderer_data(rdata)
                rdata = await self.renderer_data()
                wdata = rdata.windows[state.state]

            # Обновление режимов и панелей
            rdata = await self._update_modes_and_panels(rdata, window, data)

        file, text, reply_markup = await window.render(wdata=wdata, rdata=rdata)

        send_args = dict(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
        message = await self._send_message(mode, send_args, chat_id, message_id)
        return message, window

    async def answer(
        self,
        window: Union[str, Alert, Window],
        chat_id: int,
        data: Optional[Dict[str, Any]] = None,
        parse_mode: ParseMode = Default("parse_mode"),
        file_bytes: Optional[Dict[str, bytes]] = None,
    ) -> Tuple[Message, Window]:
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
        window: Union[str, Alert, Window],
        chat_id: int,
        message_id: int,
        data: Optional[Dict[str, Any]] = None,
        parse_mode: ParseMode = Default("parse_mode"),
        file_bytes: Optional[Dict[str, bytes]] = None,
    ) -> Tuple[Message, Window]:
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
        window: Union[str, Alert, Window],
        chat_id: int,
        message_id: int,
        data: Optional[Dict[str, Any]] = None,
        parse_mode: ParseMode = Default("parse_mode"),
        file_bytes: Optional[Dict[str, bytes]] = None,
    ) -> Tuple[Message, Window]:
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
        window: Union[str, Alert, Window],
        chat_id: int,
        message_id: int,
        data: Optional[Dict[str, Any]] = None,
        parse_mode: ParseMode = Default("parse_mode"),
        file_bytes: Optional[Dict[str, bytes]] = None,
    ) -> Tuple[Message, Window]:
        return await self.render(
            window=window,
            chat_id=chat_id,
            message_id=message_id,
            parse_mode=parse_mode,
            mode=RenderMode.REPLY,
            data=data,
            file_bytes=file_bytes,
        )
