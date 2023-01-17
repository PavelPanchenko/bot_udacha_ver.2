from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

_CALLBACK_DATA_PREFIX = 'r_c'
REASON_CALLBACK = CallbackData(_CALLBACK_DATA_PREFIX, 'name', 'guid')

post_or_edit = InlineKeyboardMarkup()
post_or_edit.add(InlineKeyboardButton(text='Редактировать', callback_data='rc_edit'))
post_or_edit.insert(InlineKeyboardButton(text='Отправить', callback_data='rc_post'))

error_events = InlineKeyboardMarkup()
error_events.add(InlineKeyboardButton(text='Создать другие событие этому клиенту', callback_data='new_event'))
