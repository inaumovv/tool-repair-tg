from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Order
from repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository):
    model: Order = Order

