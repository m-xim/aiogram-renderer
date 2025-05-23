from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from example.windows import alert_mode
from filters import IsMode
from renderer import Renderer
from states import MenuStates

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


@router.message(F.text.in_({"/start", "/restart"}))
async def start(message: Message, renderer: Renderer):
    await renderer.answer(
        window=MenuStates.main,
        chat_id=message.chat.id,
        data={"username": f" {message.from_user.username}" if message.from_user else "",
              "test_when": False,
              "path": "test23225",
              "test_dg": {
                  "page": 2,
                  "text": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"],
                  "data": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]},
              "test_dg2": {
                  "page": 2,
                  "text": ["3", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"],
                  "data": ["3", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]}},
    )


@router.callback_query(IsMode("decoder_h264"))
async def start2(callback: CallbackQuery, state: FSMContext, renderer: Renderer):
    print(1)
    mode_name = callback.data.replace("__mode__:", "")
    # Переключаем режим
    await renderer.bot_modes.update_mode(mode=mode_name)
    # Для InilineButtonMode бот просто отредактирует окно
    await renderer.edit(window=await state.get_state(),
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id)


@router.message(IsMode("decoder_h2"))
async def start3(message: Message, state: FSMContext, renderer: Renderer):
    print(2)
    mode = await renderer.bot_modes.get_mode_by_value(value=message.text)
    await renderer.bot_modes.update_mode(mode=mode.name)
    # Для ReplyButtonMode бот отправит окно с уведомлением
    await renderer.render(window=alert_mode, chat_id=message.chat.id)
    await message.delete()
