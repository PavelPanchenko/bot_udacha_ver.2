from pydantic import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    admins = [462509913]

    PORT: int
    HOST: str

    # database
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str = 'localhost'

    REDIS_HOST: str = 'localhost'


settings = Settings(_env_file='.env', _env_file_encoding='utf-8')
