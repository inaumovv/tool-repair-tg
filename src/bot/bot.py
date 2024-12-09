from aiogram import Bot

from src.config import settings

bot = Bot(settings.BOT_TOKEN, parse_mode="HTML")