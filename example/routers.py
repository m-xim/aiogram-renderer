from os import getcwd
import aiofiles
from aiogram import Router, F
from aiogram.types import Message
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


# @router.callback_query(IsModeName("decoder_h2"))
# @router.message(IsModeName("decoder_h2"))
# async def decoder_h2(event: Message | CallbackQuery, renderer: Renderer):
#     message = event if isinstance(event, Message) else event.message
#
#     await renderer.bot_modes.update_mode(name='decoder_h2')
#
#     # ....
#
#     if isinstance(event, CallbackQuery):
#         await renderer.delete_and_send(w_state=MenuStates.main, chat_id=message.chat.id, message_id=message.message_id)
#     else:
#         await renderer.send_alert(window=w_h2_alert, chat_id=message.chat.id)
