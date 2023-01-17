import re
from enum import Enum
from typing import Literal

from pydantic import BaseModel, validator


class NewEvent(BaseModel):
    recipient_phone: str
    client_phone: str
    client: str
    event_type: str
    site: str
    comment: str

    @validator(*['client_phone', 'recipient_phone'])
    def validate_phone_number(cls, v):
        if re.match(r"^\d{10}$", v):
            return v
        raise ValueError('Номер должен состоять из 10 цифр')


class UserRole(str, Enum):
    ADMIN = 'admin'
    AGENT = 'agent'
    MANAGER = 'manager'
    UNKNOWN = 'unknown'


LiteralUserRole: Literal['admin', 'agent', 'manager', 'unknown']


class UserCreate(BaseModel):
    tg_id: int = None
    phone_number: str
    name: str
    role: UserRole = UserRole.UNKNOWN.value


class UserOut(UserCreate):
    id: int

# class UserStateData(BaseModel):
#     auth: bool = False
