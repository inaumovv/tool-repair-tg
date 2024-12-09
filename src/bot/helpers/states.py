from aiogram.fsm.state import StatesGroup, State


class AddToolStates(StatesGroup):
    photo: State = State()
    tool_name: State = State()
    client_name: State = State()
    phone_number: State = State()
    select_option: State = State()

