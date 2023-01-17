from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

#
# def kb_status(data):
#     markup = InlineKeyboardMarkup()
#     for kb in data:
#         markup.add(InlineKeyboardButton(text=kb.NAME, callback_data=kb.NAME))
#     return markup


post_or_edit = InlineKeyboardMarkup()
post_or_edit.add(InlineKeyboardButton(text='Редактировать', callback_data='book_edit'))
post_or_edit.add(InlineKeyboardButton(text='Отправить', callback_data='book_post'))
