from contextlib import asynccontextmanager

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.results import InsertOneResult

from config import settings


class MongoDB:
    database: str = settings.MONGO_DATABASE
    client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGO_URL)

    @classmethod
    async def add(cls, collection: str, image_bytes: bytes, _id: int) -> int:
        database = cls.client[cls.database]
        collection = database[collection]
        document: dict = {'_id': _id, 'image': image_bytes}
        result: InsertOneResult = await collection.insert_one(document)
        return result.inserted_id

    @classmethod
    async def get(cls, collection: str, _id: int) -> bytes:
        database = cls.client[cls.database]
        collection = database[collection]
        document: dict = await collection.find_one({'_id': _id})
        image_bytes: bytes = document['image']
        return image_bytes
