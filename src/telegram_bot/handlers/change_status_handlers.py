from datetime import datetime
from json import tool

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.orm import joinedload, selectinload

from services.redis import AsyncRedis
from telegram_bot.helpers.keyboard import Keyboard
from telegram_bot.helpers.states import ChangeOrderStatusStates
from database import async_session_maker
from models import Order, Status
from repositories.order_repository import OrderRepository
from telegram_bot.helpers.validators import validate_price, validate_order_id, validate_deadline
from services.message_sender import WhatsAppMessageSender

router: Router = Router()


@router.message(F.text == 'Сменить статус ремонта')
async def start_change_status(
        message: Message,
        state: FSMContext,
        keyboard: Keyboard = Keyboard,
):
    await message.answer('Отправьте номер ремонта', reply_markup=keyboard.cancel_keyboard())
    await state.set_state(ChangeOrderStatusStates.id)


@router.message(ChangeOrderStatusStates.id, F.text)
async def get_order_id(
        message: Message,
        state: FSMContext,
        keyboard: Keyboard = Keyboard,
        repo: OrderRepository = OrderRepository

):
    try:
        order_id: int = await validate_order_id(message.text)
    except ValueError as e:
        await message.answer(e.args[0])
        return

    async with async_session_maker() as session:
        order: Order = await repo.get_one_or_none(session=session, id=order_id)
        await session.commit()

    if order:
        if order.status.value != 'Завершен' and order.status.value != 'Отменен' and order.status.value != 'Ремонт невозможен':
            await message.answer('Выберите статус', reply_markup=keyboard.statuses_keyboard(order.status.value))
            await state.set_state(ChangeOrderStatusStates.status)
            await state.update_data(order_id=order.id, status=order.status.value)
        else:
            await message.answer(f'Статус ремонта "{order.status.value}" невозможно изменить',
                                 reply_markup=keyboard.main_keyboard())
    else:
        await message.answer('Ремонта с таким номером не существует')


@router.message(ChangeOrderStatusStates.status, F.text == 'Ремонт невозможен')
async def set_repair_is_not_possible(
        message: Message,
        state: FSMContext,
        keyboard: Keyboard = Keyboard,
        repo: OrderRepository = OrderRepository,
        message_sender: WhatsAppMessageSender = WhatsAppMessageSender
):
    data: dict = await state.get_data()
    order_id: int = data.get('order_id')

    async with async_session_maker() as session:
        await repo.update(session, Order.id == order_id, obj_in={'status': Status.REPAIR_IS_NOT_POSSIBLE})
        order: Order = await repo.get_one_or_none(
            session, options=(joinedload(Order.client), selectinload(Order.tools)), id=order_id
        )
        await session.commit()

    tools_string = ", ".join([str_tool.name for str_tool in order.tools])

    await message_sender.send_message(
        order.client.phone,
        f'Уважаемый {order.client.name},\n'
        f'диагностика вашего инструмента завершена.\n'
        f'К сожалению, инструменты {tools_string} (заявка №{order_id}) не подлежат ремонту.'
        f'Вы можете забрать его в сервисном центре в удобное для вас время.'
    )

    await state.clear()
    await message.answer('Статус ремонта изменен на "Ремонт невозможен" и уведомили об этом клиента',
                         reply_markup=keyboard.main_keyboard())


@router.message(ChangeOrderStatusStates.status, F.text == 'Диагностика')
async def set_diagnostics_status(
        message: Message,
        state: FSMContext,
        keyboard: Keyboard = Keyboard,
        repo: OrderRepository = OrderRepository
):
    data: dict = await state.get_data()
    order_id: int = data.get('order_id')

    async with async_session_maker() as session:
        await repo.update(session, Order.id == order_id, obj_in={'status': Status.DIAGNOSTICS})
        await session.commit()

    await state.clear()
    await message.answer('Статус ремонта изменен на "Диагностика"', reply_markup=keyboard.main_keyboard())


@router.message(ChangeOrderStatusStates.status, F.text == 'Диагностика закончена')
async def set_diagnostics_completed_status(
        message: Message,
        state: FSMContext,
        keyboard: Keyboard = Keyboard,
):
    data: dict = await state.get_data()
    if message.text != data['status']:
        await message.answer('Отправьте итоговую сумму ремонта', reply_markup=keyboard.cancel_keyboard())
        await state.set_state(ChangeOrderStatusStates.price)
        await state.update_data(order_id=data['order_id'])
    else:
        await message.answer('Этот статус уже установлен.')


@router.message(ChangeOrderStatusStates.price, F.text)
async def get_order_price(
        message: Message,
        state: FSMContext
):
    try:
        await validate_price(message.text)
    except ValueError as e:
        await message.answer(e.args[0])
        return

    await state.update_data(price=message.text)
    await state.set_state(ChangeOrderStatusStates.deadline)

    await message.answer('Отправьте день сдачи в формате ДД.ММ.ГГГГ')


@router.message(ChangeOrderStatusStates.deadline, F.text)
async def get_order_deadline(
        message: Message,
        state: FSMContext,
        keyboard: Keyboard = Keyboard,
        repo: OrderRepository = OrderRepository,
        message_sender: WhatsAppMessageSender = WhatsAppMessageSender,
        redis: AsyncRedis = AsyncRedis
):
    data: dict = await state.get_data()

    try:
        deadline: datetime = await validate_deadline(message.text)
    except ValueError as e:
        await message.answer(e.args[0])
        return

    async with async_session_maker() as session:
        await repo.update(
            session,
            Order.id == data['order_id'],
            obj_in={
                'status': Status.DIAGNOSTICS_COMPLETED,
                'price': int(data['price']),
                'deadline': deadline
            }
        )
        order: Order = await repo.get_one_or_none(session, options=joinedload(Order.client), id=data['order_id'])
        await session.commit()

    await redis.set(
        order.client.phone,
        {'staff_chat_id': message.chat.id, 'order_id': order.id},
        to_json=True
    )

    message_text: str = (f'Уважаемый {order.client.name},\n'
                         f'диагностика вашего инструмента закончена.\n'
                         f'Итоговая сумма ремонта: {data["price"]}\n'
                         f'Срок сдачи: {message.text}\n\n'
                         f'Отправьте в ответном сообщении "+", если согласны на условия ремонта, '
                         f'"-" если нет.')
    await message_sender.send_message(order.client.phone, message_text)

    await message.answer(
        'Данные успешно сохранены и отправлены клиенту для подтверждения.\n'
        'При ответе вам будет отправлено уведомление о решении клиента и статус ремонта автоматически сменится на '
        '"в процессе" при положительном ответе, "отменен" при отрицательном.', reply_markup=keyboard.main_keyboard()
    )
    await state.clear()


@router.message(ChangeOrderStatusStates.status, F.text == 'В процессе')
async def set_in_progress_status(
        message: Message,
        state: FSMContext,
        repo: OrderRepository = OrderRepository,
        keyboard: Keyboard = Keyboard
):
    data: dict = await state.get_data()
    order_id: int = data.get('order_id')

    async with async_session_maker() as session:
        await repo.update(session, Order.id == order_id, obj_in={'status': Status.IN_PROGRESS})
        await session.commit()

    await state.clear()
    await message.answer('Статус ремонта изменен на "В процессе"', reply_markup=keyboard.main_keyboard())


@router.message(ChangeOrderStatusStates.status, F.text == 'Завершен')
async def set_completed_status(
        message: Message,
        state: FSMContext,
        repo: OrderRepository = OrderRepository,
        keyboard: Keyboard = Keyboard,
        message_sender: WhatsAppMessageSender = WhatsAppMessageSender
):
    data: dict = await state.get_data()
    order_id: int = data.get('order_id')

    async with async_session_maker() as session:
        await repo.update(session, Order.id == order_id, obj_in={'status': Status.COMPLETED})
        order: Order = await repo.get_one_or_none(session, options=joinedload(Order.client), id=order_id)
        await session.commit()

    await message_sender.send_message(
        order.client.phone,
        f'Уважаемый {order.client.name},\n'
        f'ремонт вашего инструмента успешно завершен.\n'
        f'Номер ремонта: {order.id}\n'
        f'Сроки хранения: до \n\n'
        f'Если вас не затруднит, оставьте, пожалуйста, отзыв о предоставленной услуге в 2gis,\n'
        f'это поможет нам улучшить сервис и предоставлять наилучшие услуги для вас!\n'
        f'https://2gis.kz/almaty/firm/70000001067099421\n\n'
    )

    await state.clear()
    await message.answer('Статус ремонта изменен на "Завершен"', reply_markup=keyboard.main_keyboard())
