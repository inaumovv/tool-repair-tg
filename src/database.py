from typing import AsyncGenerator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import settings


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=settings.DB_NAMING_CONVENTION)
    pass


async_engine = create_async_engine(settings.POSTGRES_URL, echo=True)
sync_engine = create_engine(settings.POSTGRES_URL_SYNC, echo=True)

async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)
sync_session_maker = sessionmaker(bind=sync_engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
