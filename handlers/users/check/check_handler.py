import re

from aiogram import types
from aiogram.dispatcher.filters import ChatTypeFilter, Command, Text
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import ChatType, Message

from api.services.inform_service import get_information_about
from api.services.user_service import get_user_by_tg_id
from keyboards.inline.all import button_information, callback_data_btn, who_worked_btn, check_confirm_data, cancel_btn
from loader import dp
from settings.message_templates import get_message_phone, check_message_phone, template_message_answer
from states.storage import Check
from utils.logger import logger


# Команда "Check"
@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), Command(commands='check'), state='*')
async def check(message: Message, state: FSMContext):
    user_data = await get_user_by_tg_id(message.from_user.id)
    if user_data.role == 'manager':
        return
    await state.reset_state(with_data=False)
    await message.answer(text=get_message_phone, reply_markup=cancel_btn)
    await Check.get_data_phone.set()


@dp.message_handler(state=Check.get_data_phone)
async def check_data_phone(message: types.Message, state: FSMContext):
    if not re.match(r'^\d{10}$', message.text):
        return await message.answer(text=check_message_phone, reply_markup=cancel_btn)

    await state.update_data(client_phone=message.text)
    await message.answer('Введите <b>имя</b> клиента, если не знаете отправьте любой символ')
    await Check.get_data_name.set()


@dp.message_handler(state=Check.get_data_name)
async def check_data_name(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    await state.update_data(client_name=message.text)

    village_names = await get_information_about('SITES')
    await message.answer(
        text=f'Выберите интересующий посёлок: ',
        reply_markup=await button_information(action='get_villages_check', data=village_names))


@dp.callback_query_handler(callback_data_btn.filter(action='get_villages_check'))
async def control(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(check_village=callback_data.get('payload'))
    data = await state.get_data()
    name = data['client_name']
    await call.message.edit_text(f'Кто будет работать с клиентом  {name} ?', reply_markup=who_worked_btn)


@dp.callback_query_handler(Text(equals=['agent', 'manager']))
async def who_worked(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(worked=call.data)
    await call.message.edit_text('Ваш комментарий:')
    await Check.get_comment.set()


@dp.message_handler(state=Check.get_comment)
async def get_comment(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    await state.update_data(comment=message.text)

    data = await state.get_data()
    village_names = await get_information_about('SITES')

    try:
        check_village = data['check_village']
        choice_village_name = [i.NAME for i in village_names if i.GUID in check_village]

        await message.answer(
            text=template_message_answer(
                data.get("client_phone"),
                data.get('client_name'),
                choice_village_name[0],
                data.get('comment')
            ),
            reply_markup=check_confirm_data)

    except Exception as ex:
        logger.warning(ex, exc_info=True)
