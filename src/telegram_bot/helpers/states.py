from aiogram.fsm.state import StatesGroup, State


class AddOrderStates(StatesGroup):
    photo: State = State()
    tool_name: State = State()
    client_name: State = State()
    phone_number: State = State()
    select_option: State = State()


class GetOrderStates(StatesGroup):
    order_id: State = State()


class GiveOrderStates(StatesGroup):
    order_id: State = State()


class ChangeOrderStatusStates(StatesGroup):
    id: State = State()
    status: State = State()
    price: State = State()
    deadline: State = State()