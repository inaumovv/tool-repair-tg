import json
from contextlib import asynccontextmanager

import redis
from redis.asyncio import Redis

from config import settings


class AsyncRedis:
    redis: Redis = Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1, encoding="utf-8", decode_responses=True
    )

    @classmethod
    async def get(cls, key: str) -> Redis | None:
        async with cls.redis.client() as client:
            data: any = await client.get(key)

        if data != 'null' or data is not None:
            try:
                return json.loads(data)
            except Exception:
                return data

        return None

    @classmethod
    async def set(cls, key: str, data: any, to_json: bool = False) -> bool:
        if to_json:
            try:
                for_write: bytes = json.dumps(data).encode('utf-8')
            except ValueError as e:
                return False
        else:
            for_write = data

        async with cls.redis.client() as client:
            return await client.set(key, for_write)

    @classmethod
    async def delete(cls, key):
        async with cls.redis.client() as client:
            await client.delete(key)


class SyncRedis:
    connection = redis.Redis(
        db=1, host=settings.REDIS_HOST, port=settings.REDIS_PORT, encoding="utf-8", decode_responses=True
    )

    @classmethod
    def query(cls) -> redis.Redis:
        return cls.connection

    @classmethod
    def get(cls, key) -> dict | None | redis.Redis:
        data = cls.query().get(key)

        if data != 'null' or data:
            try:
                return json.loads(data)
            except Exception:
                return data

        return None

    @classmethod
    def set(cls, key, data, to_json=False) -> redis.Redis | bool:
        if to_json:
            try:
                for_write = json.dumps(data).encode('utf-8')
            except ValueError:
                return False
        else:
            for_write = data

        return cls.query().set(key, for_write)

    @classmethod
    def delete(cls, key):
        cls.query().delete(key)
