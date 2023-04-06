from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter, Command
from aiogram.types import ChatType, Message

from loader import dp


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), Command(commands='kp'), state='*')
async def kp_command(message: Message, state: FSMContext):
    await state.reset_state(with_data=False)

    await message.answer(text='Команда в настоящий момент не доступна')
