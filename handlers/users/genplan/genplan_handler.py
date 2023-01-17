from datetime import datetime
from io import BytesIO

import requests
from aiogram.dispatcher.filters import ChatTypeFilter, Command
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import ChatType, Message, CallbackQuery, ChatActions

from api.services.inform_service import get_information_about
from keyboards.inline.all import button_information, callback_data_btn
from loader import dp
from utils.logger import logger


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), Command(commands='genplan'), state='*')
async def gen_plan(message: Message, state: FSMContext):
    await state.reset_state(with_data=False)

    villages = await get_information_about('SITES')
    if not villages:
        logger.warning(villages, exc_info=True)
    await message.answer(
        text='Выберите поселок',
        reply_markup=await button_information(action='get_plan', data=villages, type_payload='name'))


@dp.callback_query_handler(callback_data_btn.filter(action='get_plan'))
async def gen_plan_village(call: CallbackQuery, callback_data: dict, state: FSMContext):
    village = callback_data.get('payload').strip().title()
    time = datetime.now().timestamp()

    await call.message.answer_chat_action(action=ChatActions.TYPING)
    url = f'https://www.ydacha.ru/poselki/print.php?vill={village}&time={time}&view=y'
    await call.message.edit_text('Обработка данных.\nПодождите немного...')
    try:
        print(url)
        file_content = requests.get(url).content
        await call.message.answer_document(document=(f'{village}.pdf', BytesIO(file_content)))

    except Exception as ex:
        await call.message.answer(text=f'Файл {village} не найден.')
        logger.warning(ex, exc_info=True)
