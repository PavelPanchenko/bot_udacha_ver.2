from fastapi import APIRouter, HTTPException
from starlette import status

from api.schemas import NewEvent, UserOut
from api.services.user_service import get_user_by_phone_number, get_all_users
from keyboards.inline.all import fast_customer_service
from loader import bot, storage

user_rout = APIRouter(prefix='/api')


@user_rout.get('/users', response_model=list[UserOut])
async def get_users():
    return await get_all_users()


@user_rout.post('/event')
async def create_event(data: NewEvent):
    try:

        recipient = await get_user_by_phone_number(phone_number=data.recipient_phone)
        if not recipient:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Пользователя с номером {data.recipient_phone} нет в базе телеграмм бота')

        await storage.update_data(
            chat=recipient.tg_id,
            user=recipient.tg_id,
            data={'role': recipient.role, 'user_phone': data.recipient_phone, 'client_phone': data.client_phone})
        await bot.send_message(
            chat_id=recipient.tg_id,
            text=message_template.format(data.client_phone, data.client, data.event_type, data.site, data.comment),
            reply_markup=fast_customer_service(data.client_phone)
        )
        return status.HTTP_201_CREATED
    except Exception as ex:
        print(ex)
        return Exception(ex)


message_template = """
<i>На вас создано новое событие</i>:
<code>Телефон</code>: {}
<code>Клиент</code>: {}
<code>Тип</code>: {}
<code>Поселок</code>: {}
<code>Комментарий</code>: {}
"""
