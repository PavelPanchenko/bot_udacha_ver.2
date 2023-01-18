import json
import re
from datetime import datetime

import aiohttp
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.callback_data import CallbackData
from aiogram_calendar import SimpleCalendar, simple_cal_callback

from api.services.inform_service import get_information_about
from api.services.user_service import get_user_by_tg_id
from keyboards.inline.all import button_information, callback_data_btn
from loader import dp, bot
from states.storage import Booking
from utils.logger import logger
from .buttons import post_or_edit


@dp.callback_query_handler(text='booking', state='*')
async def booking_func(call: CallbackQuery):
    villages = await get_information_about('SITES')
    await call.message.answer(
        text='Выберите поселок:',
        reply_markup=await button_information(action='booking_get_villages', data=villages))


@dp.callback_query_handler(callback_data_btn.filter(action='booking_get_villages'))
async def control_book(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(book_village=callback_data.get('payload'))
    await call.message.edit_text('Введите номер участка', reply_markup=None)
    await Booking.lot_number.set()


@dp.message_handler(state=Booking.lot_number)
async def lot_number(message: types.Message, state: FSMContext):
    if not re.match(r'^\d+$', message.text):
        return await message.answer(text='Номер введен не верно!\nВведите цифровое значение')
    await state.reset_state(with_data=False)

    await state.update_data(lot=message.text.split(','))

    statuses = await get_information_about('STATUSES')

    await message.answer(
        text='Выберите вид брони:',
        reply_markup=await button_information(action='booking_statuses', data=statuses, type_payload='name'))


@dp.callback_query_handler(callback_data_btn.filter(action='booking_statuses'))
async def book_status(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await bot.answer_callback_query(call.id)

    await state.update_data(book_status=callback_data.get('payload'))
    await call.message.answer('Плановая дата сделки:', reply_markup=await SimpleCalendar().start_calendar())
    await state.set_state('get_booking_date')


@dp.callback_query_handler(simple_cal_callback.filter(), state='get_booking_date')
async def calendar_callback_handler(call: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await bot.answer_callback_query(call.id)
    await state.reset_state(with_data=False)

    selected, date = await SimpleCalendar().process_selection(call, callback_data)

    if selected:
        await state.update_data(book_date=datetime.strftime(date, '%Y-%m-%d'))
        await call.message.edit_text(text=datetime.strftime(date, '%Y-%m-%d'))

        await call.message.answer(text='Какой-то произвольный комментарий:')
        await Booking.comment_book.set()


@dp.message_handler(state=Booking.comment_book)
async def comment(message: Message, state: FSMContext):
    await state.reset_state(with_data=False)

    await state.update_data(book_comment=message.text)
    data = await state.get_data()
    choice_village_name = [i.NAME for i in await get_information_about('SITES') if i.GUID in data.get("book_village")]
    await message.answer(
        text=template_message_answer.format(
            choice_village_name[0],
            data.get("lot")[0],
            data.get("book_status"),
            data.get("book_date"),
            data.get("book_comment")),
        reply_markup=post_or_edit
    )


@dp.callback_query_handler(Text(equals=['book_edit', 'book_post']))
async def book_confirm(call: CallbackQuery, state: FSMContext):
    if call.data == 'book_edit':
        await booking_func(call)

    if call.data == 'book_post':
        await bot.answer_callback_query(call.id)
        data = await state.get_data()

        user_data = await get_user_by_tg_id(call.message.chat.id)

        await call.message.edit_text('Обработка данных.\nПодождите немного...')
        try:
            url = f'http://rdp.ydacha.ru:80/KA/hs/Agents/Reservation'
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        url=url,
                        params=await get_params_string(data, user_data)
                ) as response:
                    result = json.loads(await response.read())

            await call.message.answer(text=result[0]['MESSAGE'])

        except Exception as ex:
            await call.message.answer('Ошибка на сервере. Попробуйте позже')
            logger.error(ex, exc_info=True)


async def get_params_string(data, user_data):
    user = 'AGENT_PHONE' if user_data.role in ['admin', 'agent'] else 'MANAGER_PHONE'
    guid_book_status = ''.join([i.GUID for i in await get_information_about('STATUSES')
                                if i.NAME == data["book_status"]]).replace('#', '')
    return {
        'CLIENT_PHONE': data["client_phone"],
        user: user_data.phone_number,
        'STATUS': guid_book_status,
        'SITE': data["book_village"],
        'NUMBER': str(data["lot"]),
        'DATE_TO_DEAL': str(data["book_date"]) + 'T00:00:00',
        'COMMENT': data["book_comment"]
    }


template_message_answer = """
<b>Бронь</b>

<b>Поселок:</b> {}
<b>Номер участка:</b> {}
<b>Вид брони:</b> {}
<b>Дата сделки: </b> {}
<b>Комментарий</b> {}
"""
