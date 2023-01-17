import json
from io import BytesIO

import aiohttp
import jmespath
from PIL import Image
from aiogram import types
from aiogram.dispatcher.filters import ChatTypeFilter, Command
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import InputFile, CallbackQuery, ChatType, Message

from api.services.inform_service import get_information_about
from keyboards.inline.all import button_information, callback_data_btn
from loader import dp
from utils.logger import logger


async def get_photo(data) -> tuple[str, list]:
    for _, value in data.items():
        village = value.get('village')
        images = jmespath.search('*.imageUrl', value)
    return village, images


async def resize_image(file):
    image = Image.open(file)
    new_image = image.resize((1280, 1280))
    buf = BytesIO()
    new_image.save(buf, format='WEBP')
    return buf.getvalue()


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), Command(commands='photo'), state='*')
async def check(message: Message, state: FSMContext):
    await state.reset_state(with_data=False)

    villages = await get_information_about('SITES')
    await message.answer(
        text='Выберите поселок',
        reply_markup=await button_information(action='get_photo', data=villages, type_payload='name'))


@dp.callback_query_handler(callback_data_btn.filter(action='get_photo'))
async def check_data(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.reset_state(with_data=False)

    url = f'https://www.ydacha.ru/bot.php?vill={callback_data.get("payload")}'

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = json.loads(await response.read())

            if not result:
                return await call.message.answer('Фото не найдены. Попробуйте позже')
            village, images = await get_photo(result)
            await call.message.answer(f'Подождите пожалуйста, идет загрузка...\nВсего {len(images)} фото')

            logger.info(f'Всего {len(images)} фото')

            splits = [images[d:d + 10] for d in range(0, len(images), 10)]

            for groups in splits:
                media = types.MediaGroup()
                for link in groups:
                    async with session.get(link) as response_link:
                        content = await response_link.read()
                        bytes_image = await resize_image(BytesIO(content))
                        media.attach_photo(photo=InputFile(BytesIO(bytes_image), village))

                await call.message.answer_media_group(media=media, disable_notification=True)
            return await call.message.answer(text='Загрузка завершена ✅')
    except Exception as ex:
        logger.warning(ex, exc_info=True)
