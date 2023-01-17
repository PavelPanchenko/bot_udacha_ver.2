from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScope

from api.schemas import UserRole
from loader import bot


async def set_auth_commands(user_role, user_id):
    if user_role == UserRole.AGENT.value:
        return await bot.set_my_commands(
            commands=[
                BotCommand('check', 'Пробить клиента'),
                BotCommand('client', 'Работа с клиентом'),
                BotCommand('price', 'Прайс'),
                BotCommand('genplan', 'Генплан'),
                BotCommand('photo', 'Фото'),
            ],
            scope=BotCommandScopeChat(chat_id=user_id)
        )

    if user_role == UserRole.MANAGER.value:
        return await bot.set_my_commands(
            commands=[
                BotCommand('client', 'Работа с клиентом'),
                BotCommand('price', 'Прайс'),
                BotCommand('genplan', 'Генплан'),
                BotCommand('photo', 'Фото'),
            ],
            scope=BotCommandScopeChat(chat_id=user_id)
        )

    if user_role == UserRole.ADMIN:
        return await bot.set_my_commands(
            commands=[
                BotCommand('check', 'Пробить клиента'),
                BotCommand('client', 'Работа с клиентом'),
                BotCommand('price', 'Прайс'),
                BotCommand('genplan', 'Генплан'),
                BotCommand('photo', 'Фото'),
                BotCommand('send', 'Отправить уведомление')
            ],
            scope=BotCommandScopeChat(chat_id=user_id)
        )
