import databases
import ormar
import sqlalchemy

from api.schemas import UserRole
from settings.config import settings


DATABASE_URL = f'postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.DB_HOST}/{settings.POSTGRES_DB}'
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename: str = "users"
        orm_mode = True

    id: int = ormar.Integer(primary_key=True)
    tg_id: int = ormar.BigInteger(nullable=True)
    phone_number: str = ormar.String(min_length=10, max_length=10)
    name: str = ormar.String(max_length=100)
    role: str = ormar.String(max_length=20, choices=list(UserRole), default=UserRole.UNKNOWN.value)


class Information(ormar.Model):
    class Meta(BaseMeta):
        tablename: str = "informations"
        orm_mode = True

    id: int = ormar.Integer(primary_key=True)
    TYPE: str = ormar.String(max_length=50, nullable=True)
    NAME: str = ormar.String(max_length=255, nullable=True)
    GUID: str = ormar.String(max_length=255, nullable=True)
    PHONE: str = ormar.String(max_length=10, nullable=True)
    MANAGER: str = ormar.String(max_length=200, nullable=True)
