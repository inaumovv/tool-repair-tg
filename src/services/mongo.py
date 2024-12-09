from contextlib import asynccontextmanager

from aiogram.fsm.storage.mongo import MongoStorage
from motor.motor_asyncio import AsyncIOMotorClient

from src.config import settings


class MongoDB:

    @asynccontextmanager
    async def get_client(self) -> AsyncIOMotorClient:
        async with AsyncIOMotorClient(settings.TEST_MONGO_URL) as client:
            yield client
