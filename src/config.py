from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    BOT_TOKEN: str
    TG_API_URL: str

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DATABASE: str

    REDIS_HOST: str
    REDIS_PORT: int

    ID_INSTANCE: str
    API_TOKEN_INSTANCE: str
    WHATSAPP_API_URL: str

    @property
    def BOT_API_URL(self):
        return f'{self.TG_API_URL}/bot{self.BOT_TOKEN}'

    @property
    def POSTGRES_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def POSTGRES_URL_SYNC(self):
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    @property
    def MONGO_URL(self):
        return f'mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}/'

    @property
    def REDIS_URL(self):
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}'

    @property
    def DB_NAMING_CONVENTION(self):
        return {
            "ix": "%(column_0_label)s_idx",
            "uq": "%(table_name)s_%(column_0_name)s_key",
            "ck": "%(table_name)s_%(constraint_name)s_check",
            "fk": "%(table_name)s_%(column_0_name)s_fkey",
            "pk": "%(table_name)s_pkey",
        }

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings: Settings = Settings()
