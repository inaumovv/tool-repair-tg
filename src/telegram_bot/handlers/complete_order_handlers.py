from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.orm import joinedload

from database import async_session_maker
from models import Order, Status
from repositories.order_repository import OrderRepository
from services.message_sender import WhatsAppMessageSender
from telegram_bot.helpers.keyboard import Keyboard
from telegram_bot.helpers.states import GiveOrderStates
from telegram_bot.helpers.validators import validate_order_id

router: Router = Router()


@router.message(F.text == 'Выдать инструмент')
async def complete_order(message: Message, state: FSMContext, keyboard: Keyboard = Keyboard):
    await message.answer('Отправьте номер ремонта', reply_markup=keyboard.cancel_keyboard())
    await state.set_state(GiveOrderStates.order_id)


@router.message(GiveOrderStates.order_id, F.text)
async def get_order_id(
        message: Message,
        state: FSMContext,
        repo: OrderRepository = OrderRepository,
        message_sender: WhatsAppMessageSender = WhatsAppMessageSender,
        keyboard: Keyboard = Keyboard
):
    try:
        order_id: int = await validate_order_id(message.text)
    except ValueError as e:
        await message.answer(e.args[0])
        return

    async with async_session_maker() as session:
        order: Order = await repo.get_one_or_none(session=session, options=joinedload(Order.client), id=order_id)

        if order:
            await repo.update(
                session,
                Order.id == order_id,
                obj_in={'status': Status.ISSUED, 'issued_at': datetime.now()})
            await message.answer('Инструмент выдан', reply_markup=keyboard.main_keyboard())

            await message_sender.async_send_message(
                order.client.phone,
                f'Уважаемый {order.client.name}, спасибо, что воспользовались нашими услугами.\n'
                f'Если вас не затруднит, оставьте, пожалуйста, отзыв о предоставленной услуге в 2gis,\n'
                f'это поможет нам улучшить сервис и предоставлять наилучшие услуги для вас!\n'
                f'https://2gis.kz/almaty/firm/70000001067099421'
            )

            await state.clear()

        else:
            await message.answer('Ремонта с таким номером не существует')

        await session.commit()
