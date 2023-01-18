from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Optional, Union

from aiogram.types import User, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData, CallbackDataFilter


class WrongCallbackException(Exception):
    pass


class NotInitedException(Exception):
    pass


class Actions(Enum):
    PICK = auto()
    NEXT = auto()


@dataclass
class InlineVillageButtonData:
    chat_id: int
    data: object
    village_choice: list[str]


class InlineVillageButton:
    _CALLBACK_DATA_PREFIX = 'v'
    BASE_CALLBACK = CallbackData(_CALLBACK_DATA_PREFIX, 'action', 'data')
    CALLBACK_NEXT = BASE_CALLBACK.new(action=Actions.NEXT.name, data='-')

    def __init__(self) -> None:
        self.data: dict[int, InlineVillageButtonData] = {}

    def _get_user_info(self, chat_id: int) -> Optional[InlineVillageButtonData]:
        return self.data.get(chat_id, None)

    def _set_user_info(self, chat_id: int, user_data: Optional[InlineVillageButtonData]):
        self.data[chat_id] = user_data

    def init(self,
             chat_id: Optional[int] = None,
             data: object = None,
             village_choice: list[str] = None):

        if chat_id is None:
            chat_id = User.get_current().id

        if data is None:
            raise ValueError('Not found village')

        if village_choice is None:
            raise ValueError('Not found village_choice')

        self._set_user_info(
            chat_id,
            InlineVillageButtonData(chat_id, data, village_choice)
        )

    def is_inited(self, chat_id: Optional[int] = None):
        if chat_id is None:
            chat_id = User.get_current().id
        return self._get_user_info(chat_id) is not None

    def get_keyboard(self, chat_id: Optional[int] = None):
        if chat_id is None:
            chat_id = User.get_current().id

        if not self.is_inited(chat_id):
            raise NotInitedException('Village button is not inited property')

        user_info = self._get_user_info(chat_id)

        markup = InlineKeyboardMarkup(row_width=2)

        data = user_info.data

        for value in data:
            markup.insert(
                InlineKeyboardButton(
                    text=f'✅ {value.NAME}' if value.GUID in user_info.village_choice else value.NAME,
                    callback_data=InlineVillageButton.BASE_CALLBACK.new(action=Actions.PICK.name, data=value.GUID)))

        if user_info.village_choice: markup.add(
            InlineKeyboardButton(text='👉🏻 Далее', callback_data=InlineVillageButton.CALLBACK_NEXT))
        return markup

    def filter(self, **config) -> CallbackDataFilter:
        return InlineVillageButton.BASE_CALLBACK.filter(**config)

    def handle_callback(self, chat_id: int, callback_data: Union[Dict[str, str], str]):

        if not self.is_inited(chat_id):
            raise NotInitedException('inline_village_button is not inited property')
        if isinstance(callback_data, str):
            try:
                callback_data = InlineVillageButton.BASE_CALLBACK.parse(callback_data)
            except ValueError:
                raise WrongCallbackException

        action, data = callback_data.get('action', None), callback_data.get('data', None)
        if action is None or data is None:
            raise WrongCallbackException("No data in callback_data.")

        user_info = self._get_user_info(chat_id)

        if callback_data['action'] == Actions.PICK.name:
            return user_info.village_choice.append(
                callback_data['data']) if data not in user_info.village_choice else user_info.village_choice.remove(
                data)
        if callback_data['action'] == Actions.NEXT.name:
            return user_info.village_choice
