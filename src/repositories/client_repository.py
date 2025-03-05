from models import Client
from repositories.base_repository import BaseRepository


class ClientRepository(BaseRepository):
    model: Client = Client
