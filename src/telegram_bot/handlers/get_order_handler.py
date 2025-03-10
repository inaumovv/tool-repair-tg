import os
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto, FSInputFile
from sqlalchemy.orm import selectinload, joinedload

from database import async_session_maker
from models import Order, Status
from repositories.order_repository import OrderRepository
from telegram_bot.bot import bot
from telegram_bot.helpers.keyboard import Keyboard
from telegram_bot.helpers.states import GetOrderStates
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
        kazakh_timezone = ZoneInfo("Asia/Almaty")
        kazakh_time = order.created_at.astimezone(kazakh_timezone)
        formatted_time = kazakh_time.strftime("%d-%m-%Y %H:%M")

        if order.status == Status.COMPLETED:
            stored_days = (datetime.utcnow() - order.completed_at).days
            if stored_days > 7:
                price_of_store = 100 * (stored_days - 7)
            else:
                price_of_store = 0

        elif order.status == Status.ISSUED:
            if order.completed_at:
                stored_days = (order.issued_at - order.completed_at).days
                price_of_store = 100 * stored_days
            else:
                stored_days = 0
                price_of_store = 0

        else:
            price_of_store = 0
            stored_days = 0

        caption: str = (f'Номер ремонта: {order.id}\n'
                        f'Время создания ремонта: {formatted_time}\n'
                        f'Цена: {order.price}₸\n'
                        f'Срок сдачи: {order.deadline}\n'
                        f'Статус: {order.status.value}\n'
                        f'Дней хранения: {stored_days}\n'
                        f'Цена за хранение: {price_of_store}₸\n\n'
                        f'Клиент:\n{order.client.name}\n'
                        f'{order.client.phone}\n\n'
                        f'Инструменты:\n')
        for tool in order.tools:
            image_path = os.path.join('tool_images', f'{tool.id}.jpg')
            image: InputMediaPhoto = InputMediaPhoto(
                media=FSInputFile(image_path)
            )
            images.append(image)
            caption += f'- {tool.name}\n'

        await bot.send_media_group(message.chat.id, images)
        await message.answer(text=caption, reply_markup=keyboard.main_keyboard())
        await state.clear()

    else:
        await message.reply('Ремонта с таким номером не найдено')
