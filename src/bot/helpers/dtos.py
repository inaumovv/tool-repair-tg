import enum
from typing import List

from pydantic import BaseModel


class Tool(BaseModel):
    tool_name: str
    image: bytes


class Client(BaseModel):
    client_name: str
    phone_number: str


class Status(enum.Enum):
    IN_QUEUE = "in_queue"
    DIAGNOSTICS = "diagnostics"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(BaseModel):
    status: Status
    client: Client
    tools: List[Tool] | Tool
