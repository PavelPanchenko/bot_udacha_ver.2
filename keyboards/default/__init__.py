from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

get_number = ReplyKeyboardMarkup(resize_keyboard=True)
get_number.add(KeyboardButton(text='LOG IN', request_contact=True))

logout = ReplyKeyboardMarkup(resize_keyboard=True)
logout.add(KeyboardButton(text='LOG OUT'))

