from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


class Keyboard:

    @classmethod
    def main_keyboard(cls) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text='Найти заказ')],
                [KeyboardButton(text='Сменить статус ремонта'), KeyboardButton(text='Новый заказ')],
                [KeyboardButton(text='Отменить ремонт')]
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
