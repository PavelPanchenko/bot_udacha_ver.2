import json
import logging

import aiohttp
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.storage import FSMContext

from api.services.user_service import get_user_by_tg_id
from loader import dp
from states.storage import Check
from keyboards.inline.all import cancel_btn


@dp.callback_query_handler(Text(equals=['check_update_data', 'check_success']))
async def confirm(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=10)
    if call.data == 'check_update_data':
        await call.message.answer('Введите номер клиента', reply_markup=cancel_btn)
        return await Check.get_data_phone.set()

    if call.data == 'check_success':

        data = await state.get_data()

        user_data = await get_user_by_tg_id(call.message.chat.id)

        choice_village = data['check_village']

        request_url = 'http://rdp.ydacha.ru:80/KA/hs/Agents/Check'

        params = {
            'CLIENT_PHONE': data["client_phone"],
            'AGENT_PHONE': user_data.phone_number,
            'NAME': data['client_name'],
            'SITE': choice_village,
            'WHO': data['worked'],
            'COMMENT': data['comment']
        }

        await call.message.edit_text('Обработка данных.\nПодождите немного...')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(request_url, params=params) as response:
                    result = json.loads(await response.read())
                    return await call.message.answer(result[0]['MESSAGE'])
        except Exception as error:
            await call.message.answer('<b>Произошла ошибка</b>')
            logging.warning(error)
