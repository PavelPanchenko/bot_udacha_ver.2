import json
from datetime import datetime

import aiohttp
from aiogram import types
from aiogram.dispatcher.filters import ChatTypeFilter, Text
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import ChatType, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from aiogram_calendar import SimpleCalendar, simple_cal_callback

from api.services.inform_service import get_information_about
from api.services.user_service import get_user_by_tg_id
from keyboards.inline.VillageButtonClass import InlineVillageButton
from keyboards.inline.all import button_information, callback_data_btn, archive_post_or_edit
from loader import dp, bot
from states.storage import Archive
from utils.logger import logger
from ..repeat_contact.buttons import error_events

inline_village = InlineVillageButton()
inline_direction = InlineVillageButton()


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE), text='archive', state='*')
async def archive_handler(call: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)

    reasons = await get_information_about('REASONS')
    await call.message.answer(
        text='Выберите статус архива:',
        reply_markup=await button_information(action='callback_archive', data=reasons, type_payload='name'))


@dp.callback_query_handler(callback_data_btn.filter(action='callback_archive'))
async def reasons_handler(call: CallbackQuery, callback_data: dict, state: FSMContext):
    payload = callback_data.get('payload')
    if payload == 'ОТКАЗ':
        print(payload)
        await state.update_data(cause_archive=payload)
        reasons_refusal = await get_information_about('REFUSAL_REASONS')
        return await call.message.edit_text(
            text='Введите причину отказа:',
            reply_markup=await button_information(action='callback_refusal', data=reasons_refusal))

    if payload == 'ПЕРСПЕКТИВА':
        await state.update_data(cause_archive=payload)
        reasons_future = await get_information_about('FUTURE_REASONS')
        await call.message.edit_text(
            text='Причина перспективы:',
            reply_markup=await button_information(action='future', data=reasons_future))

    if payload == 'СПЯЩИЙ КЛИЕНТ':
        await state.update_data(cause_archive=payload)
        reasons_sleep = await get_information_about('ASLIPE_REASONS')
        await call.message.edit_text(
            text='Причина сна:',
            reply_markup=await button_information(action='callback_aslipe', data=reasons_sleep))


# Отказ
@dp.callback_query_handler(callback_data_btn.filter(action='callback_refusal'))
async def refusal(call: CallbackQuery, callback_data: dict, state: FSMContext):
    payload = callback_data.get('payload')
    choice_archive_name = [i.NAME for i in await get_information_about('REFUSAL_REASONS') if i.GUID == payload]
    arc_name = ' ,'.join(choice_archive_name)
    await state.update_data(archive_refusal={'name': arc_name, 'guid': payload})
    await call.message.edit_text('Введите комментарий:')
    await Archive.comment.set()


# Перспектива
@dp.callback_query_handler(callback_data_btn.filter(action='future'))
async def future(call: CallbackQuery, callback_data: dict, state: FSMContext):
    print(callback_data)
    try:
        payload = callback_data.get('payload')
        choice_archive_name = ' ,'.join(
            [i.NAME for i in await get_information_about('FUTURE_REASONS') if i.GUID == payload])
        await state.update_data(archive_future={'name': choice_archive_name, 'guid': payload})
        reasons_distances = await get_information_about('DISTANCES')
        await call.message.edit_text(
            text='Удаленность:',
            reply_markup=await button_information(action='archive_distances', data=reasons_distances))
    except Exception as ex:
        print(ex)


# DISTANCES
@dp.callback_query_handler(callback_data_btn.filter(action='archive_distances'))
async def distances(call: CallbackQuery, callback_data: dict, state: FSMContext):
    payload = callback_data.get('payload')
    choice_archive_name = ' ,'.join([i.NAME for i in await get_information_about('DISTANCES') if i.GUID == payload])
    await state.update_data(archive_distances={'name': choice_archive_name, 'guid': payload})

    inline_direction.init(
        chat_id=call.message.chat.id,
        data=await get_information_about('DIRECTIONS'),
        village_choice=[])
    await call.message.edit_text('Направление:', reply_markup=inline_direction.get_keyboard())
    await Archive.direction.set()


# DIRECTION
@dp.callback_query_handler(inline_direction.filter(), state=Archive.direction)
async def direction(call: CallbackQuery, callback_data: dict, state: FSMContext):
    return_data = inline_direction.handle_callback(call.from_user.id, callback_data)
    if return_data is None:
        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id, message_id=call.message.message_id,
            reply_markup=inline_direction.get_keyboard(call.from_user.id))
    else:
        await state.reset_state(with_data=False)
        await state.update_data({'archive_direction': return_data})
        price_ranges = await get_information_about('PRICE_RANGES')
        await call.message.edit_text(
            text='Диапазон цен:',
            reply_markup=await button_information(action='price_range', data=price_ranges))


# PRICE_RANGE 
@dp.callback_query_handler(callback_data_btn.filter(action='price_range'))
async def direction(call: CallbackQuery, callback_data: dict, state: FSMContext):
    payload = callback_data.get('payload')
    choice_archive_name = ' ,'.join([i.NAME for i in await get_information_about('PRICE_RANGES') if i.GUID == payload])
    await state.update_data(archive_price={'name': choice_archive_name, 'guid': payload})
    await call.message.edit_text(text='Введите комментарий:')
    await Archive.comment.set()


# Спящий клиент
@dp.callback_query_handler(callback_data_btn.filter(action='callback_aslipe'))
async def sleep_client(call: CallbackQuery, callback_data: dict, state: FSMContext):
    payload = callback_data.get('payload')
    choice_archive_name = ' ,'.join(
        [i.NAME for i in await get_information_about('ASLIPE_REASONS') if i.GUID == payload])
    await state.update_data(status_aspile={'name': choice_archive_name, 'guid': payload})
    await call.message.edit_text('Дата последнего созвона:', reply_markup=await SimpleCalendar().start_calendar())
    await Archive.calendar.set()


@dp.callback_query_handler(simple_cal_callback.filter(), state=Archive.calendar)
async def calendar_callback_handler(call: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await bot.answer_callback_query(call.id)

    selected, date = await SimpleCalendar().process_selection(call, callback_data)

    if selected:
        await state.update_data(archive_date=datetime.strftime(date, '%Y-%m-%d'))
        await call.message.edit_text(text=datetime.strftime(date, '%Y-%m-%d'))
        villages = await get_information_about("SITES")
        inline_village.init(chat_id=call.message.chat.id, data=villages, village_choice=[])
        await call.message.edit_text('Поселки для архива:', reply_markup=inline_village.get_keyboard())
        await Archive.village.set()


@dp.callback_query_handler(inline_village.filter(), state=Archive.village)
async def control_book(call: CallbackQuery, callback_data: dict, state: FSMContext):
    return_data = inline_village.handle_callback(call.from_user.id, callback_data)
    if return_data is None:
        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id, message_id=call.message.message_id,
            reply_markup=inline_village.get_keyboard(call.from_user.id))
    else:
        await state.update_data({'archive_vill': return_data})
        await call.message.edit_text('Введите комментарий:', reply_markup=None)
        await Archive.comment.set()


@dp.message_handler(state=Archive.comment)
async def archive_comment(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)

    try:
        await state.update_data(archive_comment=message.text)
        data = await state.get_data()

        msg = f'<b>Архив</b>\n\n' \
              f'<b>Статус:</b> {data["cause_archive"]}\n'

        if data["cause_archive"] == 'ОТКАЗ':
            msg += f'<b>Причина отказа:</b> {data["archive_refusal"]["name"]}\n'

        if data["cause_archive"] == 'ПЕРСПЕКТИВА':
            choice_direction_name = ', '.join(
                [i.NAME for i in await get_information_about('DIRECTIONS') if i.GUID in data["archive_direction"]])
            msg += f'<b>Причина перспективы:</b> {data["archive_future"]["name"]}\n' \
                   f'<b>Удаленность:</b> {data["archive_distances"]["name"]}\n' \
                   f'<b>Направление:</b> {choice_direction_name}\n' \
                   f'<b>Диапазон цен:</b> {data["archive_price"]["name"]}\n'

        if data["cause_archive"] == 'СПЯЩИЙ КЛИЕНТ':
            choice_village_name = ', '.join(
                [i.NAME for i in await get_information_about('SITES') if i.GUID in data["archive_vill"]])
            msg += f'<b>Причина сна:</b> {data["status_aspile"]["name"]}\n' \
                   f'<b>Дата последнего созвона:</b> {data["archive_date"]}\n' \
                   f'<b>Поселки:</b> {choice_village_name}\n'

        msg += f'<b>Комментарий:</b> {data["archive_comment"]}'
        await message.answer(msg, reply_markup=archive_post_or_edit)
    except Exception as ex:
        print('Error archive_comment:', ex)


@dp.callback_query_handler(Text(equals=['archive_post', 'archive_edit']))
async def book_confirm(call: CallbackQuery, state: FSMContext):
    if call.data == 'archive_edit':
        return await archive_handler(call, state)

    if call.data == 'archive_post':
        data = await state.get_data()

        user_data = await get_user_by_tg_id(call.message.chat.id)

        guid_archive_status = ''.join(
            [i.GUID for i in await get_information_about('REASONS') if i.NAME == data["cause_archive"]]).replace(
            '#', '')
        url = f'http://rdp.ydacha.ru:80/KA/hs/Agents/Archive?' \
              f'CLIENT_PHONE={data["client_phone"]}&MANAGER_PHONE={user_data.phone_number}' \
              f'&REASON={guid_archive_status}'

        if data["cause_archive"] == 'ОТКАЗ':
            url += f'&REFUSAL_REASON={data["archive_refusal"]["guid"]}'

        if data["cause_archive"] == 'ПЕРСПЕКТИВА':
            url += f'&FUTURE_REASON={data["archive_future"]["guid"]}' \
                   f'&DISTANCE={data["archive_distances"]["guid"]}' \
                   f'&DIRECTION={data["archive_direction"]}' \
                   f'&PRICE_RANGE={data["archive_price"]["guid"]}'  # origin

        if data["cause_archive"] == 'СПЯЩИЙ КЛИЕНТ':
            url += f'&ASLIPE_REASON={data["status_aspile"]["guid"]}' \
                   f'&LAST_CALL_DATE={data["archive_date"]}T00:00:00' \
                   f'&SITES_ARCH={data["archive_vill"]}'

        url += f'&TEXT={data["archive_comment"]}'

    await call.message.edit_text('Обработка данных.\nПодождите немного...')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.read()
                result = json.loads(data)

        await call.message.answer(
            text=result[0]['MESSAGE'],
            reply_markup=None if 'ERROR' in result[0] else error_events)

        await state.reset_state(with_data=False)

    except Exception as ex:
        await call.message.answer('Ошибка на сервере. Попробуйте позже')
        logger.error(ex, exc_info=True)
