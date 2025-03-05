from typing import Any, Generic, TypeVar, List, Dict, Sequence

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update, Row, RowMapping, Select, Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import _AbstractLoad

from database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    model = None

    @classmethod
    async def get_one_or_none(
            cls,
            session: AsyncSession,
            options: tuple | _AbstractLoad | None = None,
            *filter,
            **filter_by
    ) -> ModelType | None:
        query: Select = select(cls.model).filter(*filter).filter_by(**filter_by)
        if options:
            query = query.options(*options) if type(options) is tuple else query.options(options)
        result: Result = await session.execute(query)
        return result.scalars().one_or_none()

    @classmethod
    async def get_all(cls, session: AsyncSession, *filter, **filter_by):
        query = select(cls.model).filter(*filter).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def add(cls, session: AsyncSession, obj_in: CreateSchemaType | dict[str, Any]) -> ModelType | None:
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump(exclude_unset=True)
        try:
            statement = insert(cls.model).values(**create_data).returning(cls.model)
            result = await session.execute(statement)
            return result.scalars().first()
        except (SQLAlchemyError, Exception) as e:
            print(e)
            return None

    @classmethod
    async def delete(cls, session: AsyncSession, *filter, **filter_by) -> None:
        statement = delete(cls.model).filter(*filter).filter_by(**filter_by)
        await session.execute(statement)

    @classmethod
    async def update(cls, session: AsyncSession, *where, obj_in: UpdateSchemaType | dict[str, Any]) -> ModelType | None:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        statement = update(cls.model).where(*where).values(**update_data).returning(cls.model)
        result = await session.execute(statement)
        return result.scalars().one()

    @classmethod
    async def add_bulk(cls, session: AsyncSession, data: List[Dict[str, Any]]):
        try:
            result = await session.execute(
                insert(cls.model).returning(cls.model),
                data
            )
            return result.scalars().all()
        except (SQLAlchemyError, Exception):
            return None
