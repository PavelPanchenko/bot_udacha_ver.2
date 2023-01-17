from datetime import datetime
from io import BytesIO

import requests
from aiogram.dispatcher.filters import ChatTypeFilter, Command
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import ChatActions, ChatType, Message, CallbackQuery

from api.services.inform_service import get_information_about
from keyboards.inline.all import button_information, callback_data_btn
from loader import dp
from utils.logger import logger


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), Command(commands='price'), state='*')
async def price(message: Message, state: FSMContext):
    await state.reset_state(with_data=False)
    villages = await get_information_about('SITES')
    await message.answer(
        text='Выберите поселок',
        reply_markup=await button_information(action='get_price', data=villages, type_payload='name'))


@dp.callback_query_handler(callback_data_btn.filter(action='get_price'))
async def check_price(call: CallbackQuery, callback_data: dict):
    village = callback_data.get('payload').strip().title()
    time = datetime.now().timestamp()

    await call.message.answer_chat_action(action=ChatActions.TYPING)
    url = f'https://www.ydacha.ru/poselki/printtable.php?name={village}&t={time}'

    await call.message.edit_text('Обработка данных.\nПодождите немного...')
    print(url)
    try:
        file_content = requests.get(url).content
        await call.message.answer_document(document=(f'{village}.pdf', BytesIO(file_content)))

    except Exception as ex:
        await call.message.answer(f'Файл {village} не найден.')
        logger.warning(ex, exc_info=True)
