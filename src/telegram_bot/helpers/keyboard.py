from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


class Keyboard:

    @classmethod
    def main_keyboard(cls) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text='Найти ремонт')],
                [KeyboardButton(text='Сменить статус ремонта'), KeyboardButton(text='Новый ремонт')],
            ]
        )

    @classmethod
    def cancel_keyboard(cls) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text='Отмена')]
            ]
        )

    @classmethod
    def select_option_keyboard(cls) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text='Добавить инструмент')],
                [KeyboardButton(text='Далее')],
                [KeyboardButton(text='Отмена')]
            ]
        )

    @classmethod
    def statuses_keyboard(cls, status: str) -> ReplyKeyboardMarkup:
        if status == 'В очереди' or status == 'Ремонт невозможен':
            return ReplyKeyboardMarkup(
                resize_keyboard=True,
                keyboard=[
                    [KeyboardButton(text='Диагностика')],
                    [KeyboardButton(text='В процессе')],
                    [KeyboardButton(text='Завершен')],
                    [KeyboardButton(text='Ремонт невозможен')],
                    [KeyboardButton(text='Отмена')]
                ]
            )

        if status == 'Диагностика':
            return ReplyKeyboardMarkup(
                resize_keyboard=True,
                keyboard=[
                    [KeyboardButton(text='Диагностика закончена')],
                    [KeyboardButton(text='Ремонт невозможен')],
                    [KeyboardButton(text='Отмена')]
                ]
            )

        if status == 'Диагностика закончена':
            return ReplyKeyboardMarkup(
                resize_keyboard=True,
                keyboard=[
                    [KeyboardButton(text='В процессе')],
                    [KeyboardButton(text='Завершен')],
                    [KeyboardButton(text='Ремонт невозможен')],
                    [KeyboardButton(text='Отмена')]
                ]
            )

        if status == 'В процессе':
            return ReplyKeyboardMarkup(
                resize_keyboard=True,
                keyboard=[
                    [KeyboardButton(text='Завершен')],
                    [KeyboardButton(text='Ремонт невозможен')],
                    [KeyboardButton(text='Отмена')]
                ]
            )
