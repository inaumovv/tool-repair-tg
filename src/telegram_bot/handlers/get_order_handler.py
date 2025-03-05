from io import BytesIO

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto, InputFile, BufferedInputFile
from sqlalchemy.orm import selectinload, joinedload

from telegram_bot.bot import bot
from telegram_bot.helpers.keyboard import Keyboard
from telegram_bot.helpers.states import GetOrderStates
from database import async_session_maker
from models import Order
from repositories.order_repository import OrderRepository
from services.mongo import MongoDB
from telegram_bot.helpers.validators import validate_order_id

router: Router = Router()


@router.message(F.text == 'Найти ремонт')
async def start_get_order(message: Message, state: FSMContext, keyboard: Keyboard = Keyboard):
    await state.set_state(GetOrderStates.order_id)
    await message.answer('Введите номер заказа', reply_markup=keyboard.cancel_keyboard())


@router.message(GetOrderStates.order_id, F.text)
async def return_order(
        message: Message,
        state: FSMContext,
        keyboard: Keyboard = Keyboard,
        order_repo: OrderRepository = OrderRepository,
        mongo: MongoDB = MongoDB
):
    images: list = []
    try:
        order_id: int = await validate_order_id(message.text)
    except ValueError as e:
        await message.answer(e.args[0])
        return

    async with async_session_maker() as session:
        order: Order = await order_repo.get_one_or_none(
            session=session, options=(selectinload(Order.tools), joinedload(Order.client)), id=order_id
        )
        await session.commit()

    if order:
        caption: str = (f'Номер ремонта: {order.id}\n'
                        f'Цена: {order.price}\n'
                        f'Срок сдачи: {order.deadline}\n'
                        f'Статус: {order.status.value}\n\n'
                        f'Клиент:\n{order.client.name}\n'
                        f'{order.client.phone}\n\n'
                        f'Инструменты:\n')
        for tool in order.tools:
            image: InputMediaPhoto = InputMediaPhoto(
                media=BufferedInputFile(await mongo.get('images', tool.id), tool.name)
            )
            images.append(image)
            caption += f'- {tool.name}\n'

        await bot.send_media_group(message.chat.id, images)
        await message.answer(text=caption, reply_markup=keyboard.main_keyboard())
        await state.clear()

    else:
        await message.reply('Ремонта с таким номером не найдено')

