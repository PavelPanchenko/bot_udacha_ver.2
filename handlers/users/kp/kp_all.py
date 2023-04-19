from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from api.services.inform_service import get_information_about
from loader import dp, bot


async def make_requests(name):
    url = f'https://www.ydacha.ru/local/ydacha/bot/presentation.php?vill={name}'

    try:
        session = await bot.get_session()
        data = await session.get(url)
        return await data.read(), name
    except Exception as ex:
        print(ex)


@dp.message_handler(Command(commands='kp'))
async def kp_command(message: Message):
    await message.answer('Обработка запроса.\nПодождите немного...')

    sites = await get_information_about('SITES')

    await message.answer(f'Найдено {len(sites)} поселка')
    count = 1
    for site in sites[:5]:
        data = await make_requests(site.NAME)
        await message.answer_document((f'{data[1]}.pdf', data[0]), caption=f'{count}/{len(sites)}')
        count += 1
    return
