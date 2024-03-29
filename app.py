import sqlalchemy
import uvicorn as uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import middlewares
from api.database.models import database, DATABASE_URL, metadata
from api.endpoints.bot_routs import bot_rout
from api.endpoints.user_routs import user_rout
from api.services.inform_service import get_information
from loader import bot, dp
from settings.config import settings
from settings.notify_admins import on_startup_notify
import handlers

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

app = FastAPI()
app.state.database = database

app.include_router(bot_rout)
app.include_router(user_rout)

WEBHOOK_PATH = f'/bot/{settings.BOT_TOKEN}'
WEBHOOK_URL = settings.HOST + WEBHOOK_PATH


@app.on_event('startup')
async def on_startup():
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()

    # await get_information()

    middlewares.setup(dp)
    await on_startup_notify(dp)

    await bot.delete_webhook()
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event('shutdown')
async def on_shutdown():
    database_ = app.state.database

    if database_.is_connected:
        await database_.disconnect()

    await bot.session.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT, use_colors=True)


# 1. Подключил postgresql вместо sqlite3
# 2. Перенес всех клиентов с файла phone_data в базу postgresql
# 3. Добавил adminer - админка для удобного доступа и управления бд
# 4. Полностью изменил структуру клиентской и серверной части. Улучшил взаимодействие с ботом.
# 5. Убрал выбор поселков в повторном контакте
# 6. Изменил логику авторизации


# 26.03.2023
# 1) При повторном контакте снова выпадает предыдущий месяц. Такое уже было
# 2) При бронировании событие бронь превращается в событие повторный контакт.
# При этом, если выбрать дату сделки в предыдущем месяце (феврале) бронь устанавливается

