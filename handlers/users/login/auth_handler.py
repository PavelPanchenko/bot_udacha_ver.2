import asyncio

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import BotCommandScopeChat

from api.schemas import UserRole, UserCreate
from api.services.user_service import get_user_by_phone_number, user_update, add_user
from keyboards import logout, get_number
from loader import dp, bot
from settings.message_templates import auth_success_message
from settings.set_bot_commands import set_auth_commands


@dp.message_handler(content_types=['contact'], state='*')
async def bot_get_contact(message: types.Message, state: FSMContext):
    await message.delete()

    phone_number = message.contact.phone_number[-10:]
    user = await get_user_by_phone_number(phone_number=phone_number)

    if not user or user and user.role == UserRole.UNKNOWN.value:
        if not user:
            await add_user(
                UserCreate(
                    tg_id=message.chat.id,
                    phone_number=str(phone_number),
                    name=message.from_user.full_name
                )
            )
        return await message.answer('Отказано в доступе! Попробуйте другой номер')

    # user_data = {'user_phone': user.phone_number}
    # await state.set_data(user_data)
    msg = await message.answer_sticker(
        sticker=r'CAACAgIAAxkBAAJNN2I3GMOSOBp9h5OH-kDsCF71w8t-AAJDAQACzRswCIC-idiBA72TIwQ')
    await asyncio.sleep(1.5)
    await bot.delete_message(chat_id=message.chat.id, message_id=msg['message_id'])

    if not user.tg_id:
        await user_update(user_id=user.id, user_data={'tg_id': message.from_user.id})

    await message.answer_photo(
        photo=open('data/images/menu_button.png', 'rb'),
        caption=auth_success_message(user_role=user.role),
        reply_markup=logout)

    await set_auth_commands(user.role, message.chat.id)


@dp.message_handler(text='LOG OUT', state='*')
async def bot_start(message: types.Message, state: FSMContext):
    await message.delete()
    await state.reset_data()
    await bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=message.chat.id))
    await message.answer('Вы вышли из системы', reply_markup=get_number)
