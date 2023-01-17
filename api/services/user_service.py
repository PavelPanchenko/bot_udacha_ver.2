from typing import Literal

from pydantic import Field

from api.database.models import User
from api.schemas import UserCreate


async def add_user(user: UserCreate) -> User:
    return await User.objects.create(**user.dict())


async def get_all_users():
    return await User.objects.all()


async def get_user_by_phone_number(phone_number: str = Field(regex=r'^\d{10}$')) -> User | None:
    return await User.objects.get_or_none(phone_number=phone_number)


async def get_user_by_tg_id(tg_id: int) -> User | None:
    return await User.objects.get_or_none(tg_id=tg_id)


async def get_user_by_role(role: Literal['agent', 'manager', 'all']) -> list[User] | None:
    if role == 'all':
        return await User.objects.exclude(role='unknown').all()
    return await User.objects.filter(role=role).all()


async def user_update(user_id: int, user_data: dict) -> User:
    user = await User.objects.get(id=user_id)
    if user:
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        return await user.update()
    else:
        raise ValueError("User not found.")
