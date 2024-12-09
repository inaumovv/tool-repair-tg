import logging

import redis
from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from src.bot.bot import bot
from src.config import settings

dispatcher: Dispatcher = Dispatcher(storage=RedisStorage(redis.Redis.from_url(settings.REDIS_URL)))
logging.basicConfig(level=logging.INFO)

logger: logging = logging.getLogger(__name__)


def _register_routers() -> None:
    pass


def _register_middleware() -> None:
    pass


@dispatcher.startup()
async def on_startup() -> None:
    # Register all routers
    _register_routers()
    _register_middleware()


def run_polling() -> None:
    dispatcher.run_polling(bot)
