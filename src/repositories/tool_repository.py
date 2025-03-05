from models import Tool
from repositories.base_repository import BaseRepository


class ToolRepository(BaseRepository):
    model: Tool = Tool
