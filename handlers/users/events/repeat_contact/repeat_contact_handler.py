import json
import random
from datetime import datetime

import aiohttp
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData
from aiogram_calendar import SimpleCalendar, simple_cal_callback

from api.services.inform_service import get_information_about
from api.services.user_service import get_user_by_tg_id
from keyboards.inline.all import client_button, button_information, callback_fast
from loader import dp, bot
from states.storage import RepeatContact
from utils.logger import logger
from .buttons import post_or_edit, error_events


@dp.callback_query_handler(text='repeat_contact', state='*')
async def repeat_contact(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=False)
    await call.message.answer(
        text='Выберите дату следующего контакта', reply_markup=await SimpleCalendar().start_calendar())


@dp.callback_query_handler(simple_cal_callback.filter())
async def calendar_callback_handler(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)

    if selected:
        try:

            await state.update_data(date_rc=datetime.strftime(date, '%Y-%m-%d'))
            await callback_query.message.edit_text(text=datetime.strftime(date, '%Y-%m-%d'))
            reasons = await get_information_about('CONTACT_REASONS')

            await callback_query.message.answer(
                text='Укажите причину контакта:',
                reply_markup=await button_information(
                    action='cause_contact', data=reasons if reasons else 'Причина не найдена')
            )
        except Exception as ex:
            print(ex)


@dp.callback_query_handler(callback_fast.filter(action='cause_contact'))
async def get_cause(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    cause_contact_id = callback_data.get('payload')
    await state.update_data(cause_contact_id=cause_contact_id)

    await call.message.edit_text('Введите комментарий:')
    await RepeatContact.comment.set()


@dp.message_handler(state=RepeatContact.comment)
async def get_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)

    data = await state.get_data()

    cause_contact_name = \
        [i.NAME for i in await get_information_about('CONTACT_REASONS') if i.GUID in data['cause_contact_id']]

    try:

        await message.answer(
            text=template_message_answer.format(
                data['date_rc'],  # Дата контакта
                cause_contact_name[0],  # Причина
                data['comment']  # Комментарий
            ),
            reply_markup=post_or_edit
        )
        await state.reset_state(with_data=False)
    except Exception as ex:
        print(ex)


@dp.callback_query_handler(Text(equals=['rc_post', 'rc_edit']))
async def confirm_data(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'rc_edit':
        await state.reset_state(with_data=False)
        await repeat_contact(call, state)

    if call.data == 'rc_post':
        data = await state.get_data()
        user_data = await get_user_by_tg_id(call.message.chat.id)

        url = f"http://rdp.ydacha.ru:80/KA/hs/Agents/Restart"

        random_village = random.choice(await get_information_about('SITES'))

        params = {
            'CLIENT_PHONE': data["client_phone"],
            'MANAGER_PHONE': user_data.phone_number,
            'NEXT_CONTACT_DATE': str(data["date_rc"]) + "T00:00:00",
            'CONTACT_REASONS': str(data["cause_contact_id"]),
            'SITES': str(random_village.GUID),
            'COMMENT': data["comment"]
        }
        await call.message.edit_text('Обработка данных.\nПодождите немного...')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url, params=params) as response:
                    result = json.loads(await response.read())
            return await call.message.answer(text=result[0]['MESSAGE'], reply_markup=error_events)

        except Exception as ex:
            await call.message.answer("Cервер не отвечает. Попробуйте позже")
            logger.warning(ex, exc_info=True)


@dp.callback_query_handler(Text(equals=['new_event']), state='*')
async def choice_client(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=False)

    user_data = await get_user_by_tg_id(call.message.chat.id)
    if call.data == 'new_event':
        await call.message.answer('Выберите действие:', reply_markup=client_button(user_data.role))


template_message_answer = """
<b>Повторный контакт</b>

<b>Дата контакта:</b> {} 
<b>Причина:</b> {} 
<b>Комментарий:</b> {} 
"""
