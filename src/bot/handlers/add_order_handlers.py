from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.helpers.keyboard import Keyboard
from src.bot.helpers.states import AddToolStates

router: Router = Router()


@router.message(F.text == 'Новый заказ')
async def start_add_order(message: Message, state: FSMContext, keyboard: Keyboard = Keyboard):
    await state.set_state(AddToolStates.photo)
    await state.update_data(tools=[None])
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
    tools[-1]['name'] = message.text
    await state.update_data(tools=tools)
    await state.set_state(AddToolStates.select_option)