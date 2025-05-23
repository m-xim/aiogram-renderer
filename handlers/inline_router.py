from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from filters import IsModeWithNotCustomHandler
from renderer import Renderer

router = Router()

# Можно использовать __disable__, __delete__
# А вот эти не стоит использовать
RESERVED_CONTAIN_CALLBACKS = ("__mode__", "__dgroup__", "__switch_to__")


@router.callback_query(F.data.startswith("__switch_to__"))
async def switch_to_window(callback: CallbackQuery, renderer: Renderer):
    open_state = callback.data.split(":")[1] + ":" + callback.data.split(":")[2]
    await renderer.edit(window=open_state, chat_id=callback.message.chat.id, message_id=callback.message.message_id)


@router.callback_query(F.data == "__disable__")
async def answer_disable_button(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "__delete__")
async def delete_callback_message(callback: CallbackQuery):
    await callback.message.delete()


@router.callback_query(IsModeWithNotCustomHandler())
async def update_mode(callback: CallbackQuery, state: FSMContext, renderer: Renderer):
    mode_name = callback.data.replace("__mode__:", "")
    # Переключаем режим
    await renderer.bot_modes.update_mode(mode=mode_name)
    # Для InilineButtonMode бот просто отредактирует окно
    await renderer.edit(window=await state.get_state(),
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id)


@router.callback_query(F.data.startswith("__dgroup__"))
async def switch_dynamic_group_page(callback: CallbackQuery, state: FSMContext, renderer: Renderer):
    page = int(callback.data.split(":")[1])
    group_name = callback.data.split(":")[2]
    message = callback.message
    w_state = await state.get_state()

    await renderer.switch_dynamic_group_page(name=group_name, page=page)
    await renderer.edit(window=w_state, chat_id=message.chat.id, message_id=message.message_id)
