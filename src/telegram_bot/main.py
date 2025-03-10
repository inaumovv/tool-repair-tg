import asyncio
import logging

from redis import asyncio as redis
from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from config import settings
from telegram_bot.bot import bot
from telegram_bot.handlers.add_order_handlers import router as add_order_router
from telegram_bot.handlers.get_order_handler import router as get_order_router
from telegram_bot.handlers.start_handler import router as start_router
from telegram_bot.handlers.change_status_handlers import router as change_status_router
from telegram_bot.handlers.complete_order_handlers import router as complete_order_router

dispatcher: Dispatcher = Dispatcher(storage=RedisStorage(redis.from_url(settings.REDIS_URL)))
logging.basicConfig(level=logging.INFO)

logger: logging = logging.getLogger(__name__)


async def _register_routers() -> None:
    dispatcher.include_routers(
        start_router,
        get_order_router,
        add_order_router,
        change_status_router,
        complete_order_router
    )


async def _register_middleware() -> None:
    pass


@dispatcher.startup()
async def on_startup() -> None:
    # Register all routers
    await _register_routers()
    await _register_middleware()


async def run_polling() -> None:
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_polling())
