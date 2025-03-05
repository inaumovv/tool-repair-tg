from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from telegram_bot.helpers.keyboard import Keyboard

router: Router = Router()


@router.message(CommandStart())
async def start(message: Message, keyboard: Keyboard = Keyboard):
    await message.answer(text='Привет!', reply_markup=keyboard.main_keyboard())


@router.message(F.text == 'Отмена')
async def cancel(message: Message, state: FSMContext, keyboard: Keyboard = Keyboard):
    await state.clear()
    await message.answer('Действие отменено', reply_markup=keyboard.main_keyboard())
