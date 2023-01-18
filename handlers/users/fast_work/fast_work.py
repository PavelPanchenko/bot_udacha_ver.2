import json
import logging

import aiohttp
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ChatActions

from api.schemas import UserRole
from api.services.user_service import get_user_by_tg_id
from keyboards.inline.all import client_button, callback_fast
from loader import dp
from utils.logger import logger


@dp.callback_query_handler(callback_fast.filter(action='fast_work'), state='*')
async def _fast_work(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.reset_state(with_data=False)

    try:
        user_data = await get_user_by_tg_id(call.message.chat.id)

        if not user_data:
            return await call.message.answer(text=not_user_data_mess)

        client_phone = callback_data.get('payload')
        await call.message.edit_text('Обработка данных.\nПодождите немного...')
        info_client = await get_info_client(user_data, client_phone)

        await call.message.answer(
            text=info_client[0]['MESSAGE'],
            reply_markup=client_button(user_data.role)
        )

    except Exception as ex:
        logging.warning(ex, exc_info=True)


async def get_info_client(user_data, client_phone):
    try:
        request_url = 'http://rdp.ydacha.ru:80/KA/hs/Agents/Info'

        params = {
            'CLIENT_PHONE': client_phone,
            'MANAGER_PHONE' if user_data.role == UserRole.MANAGER.value else 'AGENT_PHONE': user_data.phone_number
        }

        async with aiohttp.ClientSession() as s:
            async with s.get(url=request_url, params=params) as response:
                data = await response.read()
                result = json.loads(data)
    except Exception as ex:
        logger.warning(ex, exc_info=True)

    return result


not_user_data_mess = """
Что бы продолжить пользоваться ботом, 
вам нужно повторно авторизоваться.
Если не видите кнопку "LOG IN"
Остановите бота и снова запустите.
"""
