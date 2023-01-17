import json
import logging
import re

import aiohttp
from aiogram import types
from aiogram.dispatcher.filters import ChatTypeFilter, Command
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import ChatType, Message

from api.schemas import UserRole
from api.services.user_service import get_user_by_tg_id
from keyboards.inline.all import client_button, cancel_btn
from loader import dp
from settings.message_templates import check_message_phone
from states.storage import Client


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), Command(commands='client'), state='*')
async def work_with_client(message: Message, state: FSMContext):
    await state.reset_state(with_data=False)

    user_data = await get_user_by_tg_id(message.chat.id)

    message_title = 'Для получения информации по вашему клиенту введите его номер в формате 9161234567'
    if user_data.role == UserRole.MANAGER:
        message_title = 'Для получения информации и работы с вашим клиентом введите его номер в формате 9161234567'

    message_edit = await message.answer(message_title, reply_markup=cancel_btn)
    await state.update_data(message_edit=message_edit['message_id'])
    await Client.get_data.set()


@dp.message_handler(state=Client.get_data)
async def get_client_data(message: types.Message, state: FSMContext):

    if not re.match(r'^\d{10}$', message.text):
        return await message.answer(text=check_message_phone, reply_markup=cancel_btn)

    user_data = await get_user_by_tg_id(message.chat.id)
    await state.update_data(client_phone=message.text.strip())

    await message.answer(text='Обработка данных.\nПодождите немного...')

    request_url = 'http://rdp.ydacha.ru:80/KA/hs/Agents/Info'
    params = {
        'CLIENT_PHONE': message.text.strip(),
        'MANAGER_PHONE' if user_data.role == UserRole.MANAGER.value else 'AGENT_PHONE': user_data.phone_number
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=request_url, params=params) as response:
                result = json.loads(await response.read())

        await message.answer(
            text=result[0]['MESSAGE'],
            reply_markup=client_button(user_data.role))

    except Exception as ex:
        await message.answer("Ошибка на сервере... Попробуйте позже")
        logging.warning(ex, exc_info=True)
    finally:
        await state.reset_state(with_data=False)

