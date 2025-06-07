from typing import Any, List, Dict, Union, Tuple, Optional
from aiogram import Bot
from aiogram.client.default import Default
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaAudio, InputMediaVideo, InputMediaPhoto
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
        return RendererData.model_validate(data) if data else RendererData()

    async def update_renderer_data(self, data: RendererData):
        await self.fsm.update_data(renderer_data=data.model_dump(mode="json", exclude_defaults=True, warnings="none"))

    async def get_window_by_state(self, state: str) -> Window:
        for window in self.windows:
            if window._state == state:
                return window
        raise ValueError("Окно не задано в конфигурации")

    async def _update_modes_and_panels(
        self, rdata: RendererData, window: Window, data: Optional[Dict[str, Any]]
    ) -> RendererData:
        if self.bot_mode_manager and not rdata.modes:  # `not rdata.modes` для обновления 1 раз
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
            try:
                return await self.bot.edit_message_text(
                    chat_id=chat_id,
                    text=send_args["text"],
                    message_id=message_id,
                    reply_markup=send_args.get("reply_markup"),
                    parse_mode=send_args.get("parse_mode"),
                )
            except Exception:
                # Пытаемся заменить caption для медиа-сообщений
                return await self.bot.edit_message_caption(
                    chat_id=chat_id,
                    caption=send_args["text"],
                    message_id=message_id,
                    reply_markup=send_args.get("reply_markup"),
                    parse_mode=send_args.get("parse_mode"),
                )
        else:
            return await self.bot.send_message(**send_args)

    async def _send_media(
        self,
        mode: str,
        medias: List,
        send_args: dict,
        chat_id: int,
        message_id: Optional[int],
        text: str,
    ) -> Optional[List[Message]]:
        if len(medias) == 1:
            input_media = medias[0]
            input_media.caption = input_media.caption or text

            if isinstance(input_media, InputMediaPhoto):
                send_func = self.bot.send_photo
                send_kw = {"photo": input_media.media}
            elif isinstance(input_media, InputMediaVideo):
                send_func = self.bot.send_video
                send_kw = {"video": input_media.media}
            elif isinstance(input_media, InputMediaAudio):
                send_func = self.bot.send_audio
                send_kw = {"audio": input_media.media}
            else:
                send_func = self.bot.send_document
                send_kw = {"document": input_media.media}

            send_kw.update(
                {
                    "chat_id": chat_id,
                    "caption": getattr(input_media, "caption", None),
                    "reply_markup": send_args.get("reply_markup"),
                }
            )

            if mode == RenderMode.REPLY:
                send_kw["reply_to_message_id"] = message_id
                message = await send_func(**send_kw)
            elif mode == RenderMode.DELETE_AND_SEND:
                await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
                message = await send_func(**send_kw)
            elif mode == RenderMode.ANSWER:
                message = await send_func(**send_kw)
            elif mode == RenderMode.EDIT:
                message = await self.bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=send_args.get("reply_markup"),
                    media=input_media,
                )
            else:
                message = await send_func(**send_kw)
            return [message]
        else:
            # Групповая отправка
            if mode == RenderMode.REPLY:
                send_args["reply_to_message_id"] = message_id
                messages = await self.bot.send_media_group(chat_id=chat_id, media=medias)
            elif mode in {RenderMode.DELETE_AND_SEND, RenderMode.EDIT}:
                await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
                messages = await self.bot.send_media_group(chat_id=chat_id, media=medias)
            else:
                messages = await self.bot.send_media_group(chat_id=chat_id, media=medias)
            return messages

    async def render(
        self,
        window: Union[str, Alert, Window],
        chat_id: int,
        data: Optional[Dict[str, Any]] = None,
        message_id: Optional[int] = None,
        mode: str = RenderMode.ANSWER,
        parse_mode: str = Default("parse_mode"),
    ) -> Tuple[Optional[Message], Window]:
        if mode in {RenderMode.REPLY, RenderMode.DELETE_AND_SEND} and message_id is None:
            raise RuntimeError("message_id is required for REPLY and DELETE_AND_SEND modes")

        rdata = await self.renderer_data()

        wdata = data

        # Определяем окно
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

        rdata = await self.renderer_data()
        wdata = (
            rdata.windows.get(window._state.state, wdata or {}) if isinstance(window, (Window, Alert)) else wdata or {}
        )

        medias, text, reply_markup = await window.render(wdata=wdata, rdata=rdata)

        if medias:
            send_args = dict(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
            messages = await self._send_media(mode, medias, send_args, chat_id, message_id, text=text)
        else:
            send_args = dict(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
            message = await self._send_message(mode, send_args, chat_id, message_id)
            messages = [message]
        return messages, window

    async def answer(
        self,
        window: Union[str, Alert, Window],
        chat_id: int,
        data: Optional[Dict[str, Any]] = None,
        parse_mode: ParseMode = Default("parse_mode"),
    ) -> Tuple[Message, Window]:
        return await self.render(
            window=window,
            chat_id=chat_id,
            parse_mode=parse_mode,
            mode=RenderMode.ANSWER,
            data=data,
        )

    async def edit(
        self,
        window: Union[str, Alert, Window],
        chat_id: int,
        message_id: int,
        data: Optional[Dict[str, Any]] = None,
        parse_mode: ParseMode = Default("parse_mode"),
    ) -> Tuple[Message, Window]:
        return await self.render(
            window=window,
            chat_id=chat_id,
            message_id=message_id,
            parse_mode=parse_mode,
            mode=RenderMode.EDIT,
            data=data,
        )

    async def delete_and_send(
        self,
        window: Union[str, Alert, Window],
        chat_id: int,
        message_id: int,
        data: Optional[Dict[str, Any]] = None,
        parse_mode: ParseMode = Default("parse_mode"),
    ) -> Tuple[Message, Window]:
        return await self.render(
            window=window,
            chat_id=chat_id,
            message_id=message_id,
            parse_mode=parse_mode,
            mode=RenderMode.DELETE_AND_SEND,
            data=data,
        )

    async def reply(
        self,
        window: Union[str, Alert, Window],
        chat_id: int,
        message_id: int,
        data: Optional[Dict[str, Any]] = None,
        parse_mode: ParseMode = Default("parse_mode"),
    ) -> Tuple[Message, Window]:
        return await self.render(
            window=window,
            chat_id=chat_id,
            message_id=message_id,
            parse_mode=parse_mode,
            mode=RenderMode.REPLY,
            data=data,
        )
