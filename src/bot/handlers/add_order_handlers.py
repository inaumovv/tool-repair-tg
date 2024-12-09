from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.helpers.keyboard import Keyboard
from src.bot.helpers.states import AddToolStates

router: Router = Router()


@router.message(F.text == 'Новый заказ')
async def start_add_order(message: Message, state: FSMContext, keyboard: Keyboard = Keyboard):
    await state.set_state(AddToolStates.photo)
    data = await state.get_data()
    await state.update_data(tools=data['tools']) if data['tools'] else await state.update_data(tools=[None])
    await message.answer('Отправьте фото инструмента', reply_markup=keyboard.cancel_keyboard())


@router.message(AddToolStates.photo, F.photo)
async def get_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    photo_file = await photo.download()

    async with open(photo_file.name, 'rb') as file:
        photo_bytes: bytes = file.read()
        data: dict = await state.get_data()
        await state.update_data(data['tools'].append({'photo': photo_bytes}))

    await state.set_state(AddToolStates.tool_name)
    await message.answer('Отправьте название инструмента')


@router.message(AddToolStates.tool_name, F.text)
async def set_tool_name(message: Message, state: FSMContext, keyboard: Keyboard = Keyboard):
    data: dict = await state.get_data()
    tools: list = data['tools']
    tools[-1]['tool_name'] = message.text
    await state.update_data(tools=tools)
    await state.set_state(AddToolStates.select_option)

    await message.answer(
        text=('Нажмите на кнопку "Добавить инструмент" чтобы добавить еще 1 инструмент'
              'Нажмите на кнопку "Далее" чтобы продолжить создание заказа'
              'Нажмите на кнопку "Отмена" чтобы отменить создание заказа'),
        reply_markup=keyboard.select_option_keyboard()
    )


@router.message(AddToolStates.select_option, F.text == 'Добавить инструмент')
async def add_tool(message: Message, state: FSMContext):
    await start_add_order(message, state)


@router.message(AddToolStates.select_option, F.text == 'Далее')
async def start_add_client_data(message: Message, state: FSMContext, keyboard: Keyboard = Keyboard):
    await state.set_state(AddToolStates.client_name)
    await message.answer('Отправьте имя и фамилию клиента', reply_markup=keyboard.cancel_keyboard())


@router.message(AddToolStates.client_name, F.text)
async def get_client_name(message: Message, state: FSMContext):
    data: dict = await state.get_data()
    data['client_name'] = message.text
    await state.update_data(**data)
    await state.set_state(AddToolStates.phone_number)
    await message.answer('Отправьте номер телефона клиента в формате +7 (XXX) XXX XX')


@router.message(AddToolStates.phone_number, F.text)
async def get_phone_number(message: Message, state: FSMContext, keyboard: Keyboard = Keyboard):
    data: dict = await state.get_data()
    data['phone_number'] = message.text

