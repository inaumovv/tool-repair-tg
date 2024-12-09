from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_USERNAME: str
    MONGO_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def POSTGRES_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def MONGO_URL(self):
        return f"mongodb://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/"

    @property
    def TEST_MONGO_URL(self):
        return 'mongodb://localhost:27017/'

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
