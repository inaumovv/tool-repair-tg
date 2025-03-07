import os

import aiofiles
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PhotoSize

from database import async_session_maker
from models import Status, Client, Order, Tool
from repositories.client_repository import ClientRepository
from repositories.order_repository import OrderRepository
from repositories.tool_repository import ToolRepository
from telegram_bot.bot import bot
from telegram_bot.helpers.keyboard import Keyboard
from telegram_bot.helpers.states import AddOrderStates
from telegram_bot.helpers.validators import validate_phone, validate_name

router: Router = Router()


@router.message(F.text == 'Новый ремонт')
async def start_add_order(message: Message, state: FSMContext, keyboard: Keyboard = Keyboard):
    await state.set_state(AddOrderStates.photo)
    data: dict | None = await state.get_data()
    await state.update_data(tools=data['tools']) if data.get('tools') else await state.update_data(tools=[])
    await message.answer('Отправьте фото инструмента', reply_markup=keyboard.cancel_keyboard())


@router.message(AddOrderStates.photo, F.photo)
async def get_photo(message: Message, state: FSMContext):
    image: PhotoSize = message.photo[-1]
    file_id: str = image.file_id

    data: dict = await state.get_data()
    tools: list = data.get('tools')
    tools.append({'image': file_id})

    await state.set_state(AddOrderStates.tool_name)
    await state.update_data(tools=tools)

    await message.answer('Отправьте название инструмента')


@router.message(AddOrderStates.tool_name, F.text)
async def set_tool_name(message: Message, state: FSMContext, keyboard: Keyboard = Keyboard):
    data: dict = await state.get_data()
    tools: list = data.get('tools')
    tools[-1]['name'] = message.text
    await state.update_data(tools=tools)
    await state.set_state(AddOrderStates.select_option)

    await message.answer(
        text=('Нажмите на кнопку "Добавить инструмент" чтобы добавить еще 1 инструмент\n'
              'Нажмите на кнопку "Далее" чтобы продолжить создание заказа\n'
              'Нажмите на кнопку "Отмена" чтобы отменить создание заказа\n'),
        reply_markup=keyboard.select_option_keyboard()
    )


@router.message(AddOrderStates.select_option, F.text == 'Добавить инструмент')
async def add_tool(message: Message, state: FSMContext):
    await start_add_order(message, state)


@router.message(AddOrderStates.select_option, F.text == 'Далее')
async def start_add_client_data(message: Message, state: FSMContext, keyboard: Keyboard = Keyboard):
    await state.set_state(AddOrderStates.client_name)
    await message.answer('Отправьте имя и фамилию клиента', reply_markup=keyboard.cancel_keyboard())


@router.message(AddOrderStates.client_name, F.text)
async def get_client_name(message: Message, state: FSMContext):
    try:
        await validate_name(message.text)
    except ValueError as e:
        await message.answer(e.args[0])
        return

    data: dict = await state.get_data()
    data.update({'client': {'name': message.text}})
    await state.update_data(**data)
    await state.set_state(AddOrderStates.phone_number)
    await message.answer('Отправьте номер телефона клиента в формате +7')


@router.message(AddOrderStates.phone_number, F.text)
async def get_phone_number(
        message: Message,
        state: FSMContext,
        keyboard: Keyboard = Keyboard,
        client_repo: ClientRepository = ClientRepository,
        order_repo: OrderRepository = OrderRepository,
        tool_repo: ToolRepository = ToolRepository,
):
    data: dict = await state.get_data()

    try:
        phone: str = await validate_phone(message.text)
    except ValueError as e:
        await message.answer(e.args[0])
        return

    data['client']['phone'] = phone

    async with async_session_maker() as session:
        client: Client = await client_repo.get_one_or_none(session=session, phone=phone)
        if client is None:
            new_client: Client = await client_repo.add(session, data['client'])
            order: Order = await order_repo.add(session, {'status': Status.IN_QUEUE, 'client_id': new_client.id})
        else:
            order: Order = await order_repo.add(session, {'status': Status.IN_QUEUE, 'client_id': client.id})

        for tool in data['tools']:

            db_tool: Tool = await tool_repo.add(
                session,
                {
                    'name': tool['name'],
                    'order_id': order.id
                }
            )
            image = await bot.download(tool['image'])
            save_path = os.path.join('tool_images', f'{db_tool.id}.jpg')

            async with aiofiles.open(save_path, "wb") as new_file:
                await new_file.write(image.read())

            await session.commit()

        await state.clear()
        await message.answer(f'Создан ремонт №{order.id}', reply_markup=keyboard.main_keyboard())
