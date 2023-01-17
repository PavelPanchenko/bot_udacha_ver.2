from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from api.schemas import UserRole
from api.services.user_service import get_user_by_tg_id, get_user_by_role
from keyboards.inline.all import callback_data_btn, admin_buttons
from loader import dp, bot
from states.storage import Admin


@dp.message_handler(Command("send"))
async def sending_menu(message: Message, state: FSMContext):
    await state.reset_state(with_data=False)
    user_data = await get_user_by_tg_id(message.chat.id)

    if user_data.role == UserRole.ADMIN.value:
        await message.answer('Кому хотите отправить сообщение ?', reply_markup=admin_buttons)


@dp.callback_query_handler(callback_data_btn.filter(action='send_msg_from_admin'))
async def get_role(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(sending_role=callback_data.get('payload'))
    await call.message.edit_text('Введите сообщение.')
    await Admin.message.set()


@dp.message_handler(state=Admin.message)
async def get_text(message: Message, state: FSMContext):
    await state.reset_state(with_data=False)

    await state.update_data(post=message.text)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(text='Редактировать', callback_data='notify_edit'),
        InlineKeyboardButton(text='Отправить', callback_data='notify_post'),
        InlineKeyboardButton(text='Отменить', callback_data='cancel')
    )
    await message.answer(f'<b>Предпросмотр и подтверждение отправки</b>:\n{message.text}', reply_markup=markup)


@dp.callback_query_handler(Text(equals=['notify_edit', 'notify_post']))
async def solution(call: CallbackQuery, state: FSMContext):
    if call.data == 'notify_edit':
        await get_role(call, state)

    if call.data == 'notify_post':
        data = await state.get_data()
        print(data.get('sending_role'))
        users = await get_user_by_role(role=data.get('sending_role'))

        count = 0
        errors = str()
        _id = call.message.chat.id
        for user in users:
            if int(user.tg_id) == _id:
                continue
            try:
                await bot.send_message(chat_id=user.tg_id, text=data.get("post"))
                count += 1
            except Exception as ex:
                errors += f'\n=========\nОшибка отправки сообщения пользователю - {user.name}\n' \
                          f'Error: {ex}\n========='

        msg = f'Найдено пользователей: {len(users)}\n' \
              f'Успешно отправлено сообщений: {count}\n' \
              f'{errors}'

        await call.message.edit_text(msg)
