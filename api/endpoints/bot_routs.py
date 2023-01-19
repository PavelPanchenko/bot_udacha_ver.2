from aiogram import Dispatcher, Bot
from aiogram.types import Update
from fastapi import APIRouter

from loader import dp, bot
from utils.logger import logger

bot_rout = APIRouter(prefix='/bot', include_in_schema=False)


@bot_rout.post('/{BOT_TOKEN}')
async def bot_webhook(update: dict):
    try:
        telegram_update = Update(**update)
        Dispatcher.set_current(dp)
        Bot.set_current(bot)
        await dp.process_update(telegram_update)
    except Exception as ex:
        logger.warning(ex, exc_info=True)
