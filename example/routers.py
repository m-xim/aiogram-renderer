from aiogram import Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from example.windows import alert_mode
from aiogram_renderer.filters import IsMode
from aiogram_renderer.renderer import Renderer
from states import MenuStates

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


@router.message(or_f(CommandStart(), Command("restart")))
async def start(message: Message, renderer: Renderer):
    data = {
        "username": f" {message.from_user.username}" if message.from_user else "",
        "test_show_on": False,
        "test_pr": 0,
        "path": "test23225",
        "filename": "test.png",
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

    sent_message, window = await renderer.answer(window=MenuStates.main1, chat_id=message.chat.id, data=data)

    # for i in range(99):
    #     await renderer.update_progress(window=MenuStates.main1, chat_id=sent_message.chat.id, interval=0.3,
    #                                    message_id=sent_message.message_id, name="test_pr", percent=i, data=data)
    #     await sleep(0.3)


# @router.callback_query(IsMode("decoder_h263"))
# async def start2(callback: CallbackQuery, state: FSMContext, renderer: Renderer):
#     print(1)
#     mode_name = callback.data.replace("__mode__:", "")
#     # Переключаем режим
#     await renderer.bot_modes.update_mode(mode=mode_name)
#     # Для InilineButtonMode бот просто отредактирует окно
#     await renderer.edit(window=await state.get_state(),
#                         chat_id=callback.message.chat.id,
#                         message_id=callback.message.message_id)


@router.message(IsMode("decoder_h2"))
async def start3(message: Message, state: FSMContext, renderer: Renderer):
    print(2)
    mode = await renderer.bot_modes.get_mode_by_value(value=message.text)
    await renderer.bot_modes.update_mode(mode=mode.name)
    # Для ReplyButtonMode бот отправит окно с уведомлением
    await renderer.render(window=alert_mode, chat_id=message.chat.id)
    await message.delete()
