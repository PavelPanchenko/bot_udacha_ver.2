from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from keyboards.inline.VillageButtonClass import InlineVillageButton
from settings.config import settings


bot = Bot(token=settings.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2(host=settings.REDIS_HOST)
dp = Dispatcher(bot, storage=storage)
inline_village_btn = InlineVillageButton()
