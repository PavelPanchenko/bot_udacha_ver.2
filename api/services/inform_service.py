import json
from datetime import datetime, timedelta

import aiohttp

from api.database.models import Information
from utils.logger import logger

star_date = datetime.now() + timedelta(seconds=10)


async def get_information():
    base_url = 'http://rdp.ydacha.ru:80/KA/hs/Agents/References'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as response:
                data = await response.read()
                items = json.loads(data)

                if items:
                    await Information.objects.delete(each=True)

                for item in items:
                    await Information.objects.create(**item)
    except Exception as error:
        logger.warning(error, exc_info=True)


async def get_information_about(type_information: str):
    try:
        return await Information.objects.filter(TYPE=type_information).all()
    except Exception as ex:
        logger.warning(ex, exc_info=True)


async def get_archive_reasons():
    return await Information.objects.filter(TYPE='REASONS').all()
