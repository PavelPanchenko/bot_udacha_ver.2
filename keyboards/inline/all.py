from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from api.schemas import UserRole

callback_fast = CallbackData('btn', 'action', 'payload')
callback_data_btn = CallbackData('btn', 'action', 'payload')


# Главное меню
def client_button(user_role: str):
    markup = InlineKeyboardMarkup(row_width=3)
    if user_role in (UserRole.MANAGER.value, UserRole.ADMIN.value):
        markup.add(InlineKeyboardButton(text='Повторный контакт', callback_data='repeat_contact'))
        markup.add(InlineKeyboardButton(text='Архив', callback_data='archive'))

    markup.insert(InlineKeyboardButton(text='Бронь', callback_data='booking'))
    return markup


# Команда check
who_worked_btn = InlineKeyboardMarkup(row_width=2)
who_worked_btn.add(InlineKeyboardButton(text='Я, агент', callback_data='agent'))
who_worked_btn.add(InlineKeyboardButton(text='Менеджер удачи', callback_data='manager'))

check_confirm_data = InlineKeyboardMarkup(row_width=2)
check_confirm_data.add(InlineKeyboardButton(text='Редактировать', callback_data='check_update_data'))
check_confirm_data.add(InlineKeyboardButton(text='Продолжить', callback_data='check_success'))

cancel_btn = InlineKeyboardMarkup(row_width=3)
cancel_btn.add(InlineKeyboardButton(text='Отмена', callback_data='cancel'))


# Для работы с событиями
def fast_customer_service(client_phone: str):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        text='Работа с клиентом',
        callback_data=callback_fast.new(action='fast_work', payload=client_phone)
    ))
    return markup


# Получение информации с information table
async def button_information(action: str, data: list, type_payload: str = 'guid'):
    markup = InlineKeyboardMarkup()
    for i in data:
        markup.add(InlineKeyboardButton(
            text=i.NAME,
            callback_data=callback_data_btn.new(
                action=action,
                payload=i.GUID if type_payload == 'guid' else i.NAME)))
    return markup


# Меню - archive
callback_archive = CallbackData('archive_status', 'action', 'payload')

post_or_edit = InlineKeyboardMarkup(row_width=2)
post_or_edit.add(InlineKeyboardButton(text='Редактировать', callback_data='book_edit'))
post_or_edit.insert(InlineKeyboardButton(text='Отправить', callback_data='book_post'))

archive_post_or_edit = InlineKeyboardMarkup(row_width=2)
archive_post_or_edit.add(InlineKeyboardButton(text='Редактировать', callback_data='archive_edit'))
archive_post_or_edit.insert(InlineKeyboardButton(text='Отправить', callback_data='archive_post'))

# Admin btn

admin_buttons = InlineKeyboardMarkup(row_width=2)
admin_buttons.add(
    InlineKeyboardButton(
        text='Агентам',
        callback_data=callback_data_btn.new(action='send_msg_from_admin', payload='agent')),
    InlineKeyboardButton(
        text='Менеджерам',
        callback_data=callback_data_btn.new(action='send_msg_from_admin', payload='manager')),
    InlineKeyboardButton(
        text='Всем',
        callback_data=callback_data_btn.new(action='send_msg_from_admin', payload='all'))
)
