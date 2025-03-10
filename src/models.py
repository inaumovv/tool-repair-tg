import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, TIMESTAMP, func, Enum, ForeignKey, text
from sqlalchemy.orm import Mapped, MappedColumn, relationship

from database import Base


class Status(enum.Enum):
    IN_QUEUE = "В очереди"
    DIAGNOSTICS = "Диагностика"
    DIAGNOSTICS_COMPLETED = "Диагностика закончена"
    IN_PROGRESS = "В процессе"
    COMPLETED = "Завершен"
    ISSUED = "Выдан"
    CANCELLED = "Отменен"
    REPAIR_IS_NOT_POSSIBLE = "Ремонт невозможен"


class Client(Base):
    __tablename__ = 'client'

    id: Mapped[int] = MappedColumn(primary_key=True)
    name: Mapped[str] = MappedColumn(String(length=128))
    phone: Mapped[str]
    orders: Mapped[List['Order']] = relationship(back_populates='client')
    created_at: Mapped[datetime] = MappedColumn(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = MappedColumn(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.utcnow)


class Order(Base):
    __tablename__ = 'order'

    id: Mapped[int] = MappedColumn(primary_key=True)
    status: Mapped[Status]
    price: Mapped[Optional[int]]
    deadline: Mapped[Optional[datetime]]
    client_id: Mapped[int] = MappedColumn(ForeignKey('client.id'))
    client: Mapped['Client'] = relationship(back_populates='orders')
    tools: Mapped[List['Tool']] = relationship(back_populates='order')
    completed_at: Mapped[Optional[datetime]] = MappedColumn(default=None)
    issued_at: Mapped[Optional[datetime]] = MappedColumn(default=None)
    last_notif_at: Mapped[Optional[datetime]] = MappedColumn(default=None)
    created_at: Mapped[datetime] = MappedColumn(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = MappedColumn(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.utcnow)


class Tool(Base):
    __tablename__ = 'tool'

    id: Mapped[int] = MappedColumn(primary_key=True)
    name: Mapped[str] = MappedColumn(String(length=128))
    order_id: Mapped[int] = MappedColumn(ForeignKey('order.id'))
    order: Mapped['Order'] = relationship(back_populates='tools')
    created_at: Mapped[datetime] = MappedColumn(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = MappedColumn(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.utcnow)