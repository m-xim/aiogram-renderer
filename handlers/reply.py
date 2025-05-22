from aiogram import Router
from aiogram.types import Message
from filters import IsUpdateModeMessage, HasNotCustomHandler, HasBotModes
from renderer import Renderer

router = Router()


@router.message(HasBotModes(), HasNotCustomHandler(), IsUpdateModeMessage())
async def update_mode(event: Message, renderer: Renderer):
    name_mode = await renderer.bot_modes.update_mode(event=event)
    # Для ReplyButtonMode бот отправит окно с уведомлением
    window = renderer.bot_modes.dict_modes[name_mode].alert_window
    await renderer.render(window=window, chat_id=event.chat.id)
    await event.delete()
