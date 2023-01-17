from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from loader import dp, bot


@dp.callback_query_handler(text='cancel', state='*')
async def cancel(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=False)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await call.message.answer('Действие отменено')
