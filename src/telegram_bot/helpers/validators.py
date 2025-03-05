import re
from datetime import datetime


async def validate_phone(phone: str) -> str:
    reformatted_phone: str = (phone.replace("-", "").replace("+", "")
                              .replace("(", "").replace(")", "").replace(" ", ""))

    if not phone.startswith('+7'):
        raise ValueError('Номер телефона должен начинаться с +7')

    if 11 > len(reformatted_phone):
        raise ValueError('Номер телефона слишком короткий')

    if 30 < len(reformatted_phone):
        raise ValueError('Номер телефона слишком длинный')

    try:
        return str(int(reformatted_phone))
    except Exception:
        raise ValueError('Номер телефона должен содержать только цифры')


async def validate_name(name: str):
    if len(name) < 2 or len(name) > 50:
        raise ValueError('Недопустимая длинна имени')

    if not re.fullmatch(r"[a-zA-Zа-яА-ЯёЁ\-' ]+", name):
        raise ValueError('Имя содержит недопустимые символы')

    if "  " in name:
        raise ValueError('Несколько пробелов подряд')


async def validate_price(price: str):
    try:
        int(price)
    except Exception:
        raise ValueError('Цена должна состоять только из цифр')


async def validate_order_id(order_id: str):
    try:
        order_id: int = int(order_id)
        return order_id
    except Exception:
        raise ValueError('Номер заказа должен быть целым числом')


async def validate_deadline(deadline: str):
    date_list: list[str] = deadline.split('.')
    if len(date_list) != 3:
        raise ValueError('Неправильный формат ввода даты.\n'
                         'Пример: 13.12.2025')
    try:
        date_1: int = int(date_list[0])
        date_2: int = int(date_list[1])
        date_3: int = int(date_list[2])

        return datetime(day=date_1, month=date_2, year=date_3)
    except Exception:
        raise ValueError('Неправильный формат ввода даты.\n'
                         'Пример: 13.12.2025')

