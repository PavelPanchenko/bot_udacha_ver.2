import asyncio
import io

import aiohttp
from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from api.services.inform_service import get_information_about
from loader import dp, bot


async def get_data_from_server(name, chat_id):
    link = f'https://www.ydacha.ru/local/ydacha/bot/presentation.php?vill={name}'
    await bot.send_document(chat_id, link, caption=name)


async def create_tasks(chat_id):
    tasks = []
    villages = await get_information_about('SITES')
    for village in villages:
        task = asyncio.create_task(get_data_from_server(village.NAME, chat_id))
        tasks.append(task)
    return asyncio.gather(*tasks)


@dp.message_handler(Command(commands='kp'))
async def kp_command(message: Message):
    await message.answer('Подождите немного...')
    chat_id = message.chat.id
    await create_tasks(chat_id)

