import aiohttp
import requests
from aiogram import Bot

from config import settings
from telegram_bot.bot import bot


class WhatsAppMessageSender:

    @classmethod
    async def async_send_message(cls, number: str, message: str):
        url: str = f'{settings.WHATSAPP_API_URL}/waInstance{settings.ID_INSTANCE}/sendMessage/{settings.API_TOKEN_INSTANCE}'
        params: dict = {
            'chatId': f'{number}@c.us',
            'message': message
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    return None

    @classmethod
    def sync_send_message(cls, number: str, message: str):
        url: str = f'{settings.WHATSAPP_API_URL}/waInstance{settings.ID_INSTANCE}/sendMessage/{settings.API_TOKEN_INSTANCE}'
        params: dict = {
            'chatId': f'{number}@c.us',
            'message': message
        }
        response = requests.post(url, json=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None


class TelegramMessageSender:
    bot: Bot = bot

    @classmethod
    def send_message(cls, chat_id: int, message: str):
        url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
        params: dict = {
            "chat_id": chat_id,
            "text": message,
        }
        requests.get(url, params=params)
