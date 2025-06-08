import logging
import asyncio
from os import getenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv

from textcompose import Template
from textcompose.elements import Text, Format, ProgressBar

from aiogram_renderer.configure import configure_renderer
from aiogram_renderer.bot_mode import BotMode
from aiogram_renderer.widgets.keyboard.inline import ComeTo, Mode, InlineButton, InlinePanel, DynamicPanel
from aiogram_renderer.widgets.media.group import MediaGroup
from aiogram_renderer.widgets.media.media import Media
from aiogram_renderer.windows.window import Window, Alert
from aiogram_renderer.renderer import Renderer

from aiogram.fsm.state import StatesGroup, State


class AppStates(StatesGroup):
    menu = State()
    loading = State()
    media_group = State()


menu_window = Window(
    Template(Text("Главное меню")),
    InlinePanel(
        Mode(name="view"),
        InlineButton(text="Показать загрузку", callback_data="progress"),
        ComeTo(text="Перейти в медиа группу (кнопки пропадут)", state=AppStates.media_group),
    ),
    DynamicPanel(name="test_dg", width=2, height=2, hide_number_pages=True),
    state=AppStates.menu,
)

progress_window = Window(
    Template(
        Text("Загрузка файла"),
        ProgressBar(current=Format("{progress}"), total=100, width=10),
    ),
    Media(path=r"example/test.png", media_type=ContentType.PHOTO),
    state=AppStates.loading,
)


media_group_window = Window(
    Template(
        Text("Медиа группа"),
    ),
    MediaGroup(
        # В Media можно указать caption для каждого элемента
        Media(path=Format(r"example/test.png"), media_type=ContentType.PHOTO),
        Media(path=Format(r"example/img.png"), media_type=ContentType.PHOTO),
    ),
    state=AppStates.media_group,
)

done_alert = Alert(
    Template(Text("Загрузка завершена!")),
)

router = dp = Dispatcher(storage=MemoryStorage())


@router.message(CommandStart())
async def cmd_start(message: Message, renderer: Renderer) -> None:
    data = {
        "username": f" {message.from_user.username}" if message.from_user else "",
        "test_dg": {
            "page": 2,
            "text": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"],
            "data": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"],
        },
        "test_dg2": {
            "page": 2,
            "text": ["3", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"],
            "data": ["3", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"],
        },
    }

    sends_message, window = await renderer.answer(window=AppStates.menu, data=data, chat_id=message.chat.id)


@router.callback_query(F.data == "progress")
async def update_progress(callback: CallbackQuery, renderer: Renderer) -> None:
    message = callback.message
    data = {"progress": 0}
    sends, _ = await renderer.answer(
        window=AppStates.loading,
        chat_id=message.chat.id,
        data=data,
    )
    sent = sends[0]
    for i in range(1, 101, 10):
        await asyncio.sleep(0.45)
        data["progress"] = i
        try:
            await renderer.edit(
                window=AppStates.loading,
                chat_id=sent.chat.id,
                message_id=sent.message_id,
                data=data,
            )
        except Exception as e:
            logging.error(f"Error updating progress: {e}")
    await renderer.render(window=done_alert, chat_id=sent.chat.id)
    await message.delete()


async def main(token: str) -> Dispatcher:
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    logging.basicConfig(level=logging.INFO)
    await configure_renderer(
        dp=dp,
        windows=[menu_window, progress_window, media_group_window],
        modes=[BotMode(name="view", values=["Просмотр", "Закрыть"])],
    )
    await dp.start_polling(bot)

    return dp


if __name__ == "__main__":
    load_dotenv()
    BOT_TOKEN = getenv("TOKEN")
    asyncio.run(main(BOT_TOKEN))
