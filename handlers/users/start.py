from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter, CommandStart
from aiogram.types import ChatType, Message, BotCommandScopeChat

from api.schemas import UserRole
from api.services.user_service import get_user_by_tg_id
from keyboards import logout, get_number
from loader import dp, bot


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), CommandStart(), state='*')
async def bot_start(message: Message, state: FSMContext):
    print(await state.get_state())
    await message.delete()
    await state.reset_state(with_data=False)

    # user_data = await state.get_data()
    user_data = await get_user_by_tg_id(message.chat.id)

    if user_data and user_data.role is not UserRole.UNKNOWN:
        return await message.answer(
            text='Вы уже авторизированны!\nВыберите пункт из меню, с которым хотите работать',
            reply_markup=logout
        )

    await bot.delete_my_commands(BotCommandScopeChat(chat_id=message.chat.id))
    await message.answer_photo(
        photo=open('data/images/login.png', 'rb'),
        caption='Добро пожаловать!\nЧто бы работать с ботом нужно авторизоваться c помощью кнопки\n"LOG IN"',
        reply_markup=get_number)
