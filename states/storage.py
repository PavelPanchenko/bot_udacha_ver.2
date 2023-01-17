from aiogram.dispatcher.filters.state import State, StatesGroup


class Contact(StatesGroup):
    number = State()
    status = State()
    phone = State()


class Check(StatesGroup):
    get_data_phone = State()
    get_data_name = State()
    get_data_village = State()
    get_who_worked = State()
    get_comment = State()
    confirm = State()
    change_data = State()
    get_server = State()


class Genplan(StatesGroup):
    get_data = State()


class Photo(StatesGroup):
    get_photo = State()


class Price(StatesGroup):
    get_data = State()


class Message(StatesGroup):
    message_id = State()


class Booking(StatesGroup):
    village = State()
    lot_number = State()
    status_book = State()
    calendar = State()
    comment_book = State()
    book_confirm = State()


class Archive(StatesGroup):
    reasone = State()
    refusal = State()
    future = State()
    aspile = State()
    calendar = State()
    village = State()
    distances = State()
    direction = State()
    price = State()
    comment = State()
    confirm = State()


class Admin(StatesGroup):
    sending = State()
    message = State()
    post = State()


class Client(StatesGroup):
    get_data = State()


class RepeatContact(StatesGroup):
    date = State()
    contact_reason = State()
    # get_village = State()
    comment = State()
    confirm = State()
