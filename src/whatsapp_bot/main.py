from sqlalchemy import update
from whatsapp_chatbot_python import GreenAPIBot, filters, Notification

from config import settings
from database import sync_session_maker
from models import Order, Status
from services.message_sender import TelegramMessageSender
from services.redis import SyncRedis

green_api_bot: GreenAPIBot = GreenAPIBot(
    id_instance=settings.ID_INSTANCE,
    api_token_instance=settings.API_TOKEN_INSTANCE,
    bot_debug_mode=True
)


@green_api_bot.router.message(types_message=filters.TEXT_TYPES, state=None, text_message='+')
def confirmation_order(notification: Notification, redis: SyncRedis = SyncRedis):
    chat_id: list[str] = notification.chat.split('@')
    key: str = chat_id[0]

    data: dict = redis.get(key)
    if data:
        staff_chat_id: int = data['staff_chat_id']
        order_id: int = data['order_id']

        send_confirm_message(staff_chat_id, order_id)

        notification.answer(
            'Условия ремонта успешно подтверждены!\n'
            'Инструменты находятся в процессе ремонта.'
        )

        redis.delete(key)

    else:
        pass


@green_api_bot.router.message(types_message=filters.TEXT_TYPES, state=None, text_message='-')
def cancellation_order(notification: Notification, redis: SyncRedis = SyncRedis):
    chat_id: list[str] = notification.chat.split('@')
    key: str = chat_id[0]

    data: dict = redis.get(key)
    if data:
        staff_chat_id: int = data['staff_chat_id']
        order_id: int = data['order_id']

        send_cancel_message(staff_chat_id, order_id)

        notification.answer(
            'Ремонт успешно отменен.\n'
            'Сроки хранения'
        )

        redis.delete(key)
    else:
        pass


def send_confirm_message(
        chat_id: int,
        order_id: int,
        message_sender: TelegramMessageSender = TelegramMessageSender
):
    session = sync_session_maker()
    session.execute(update(Order).where(Order.id == order_id).values({'status': Status.IN_PROGRESS}))
    session.commit()
    session.close()

    message_sender.send_message(
        chat_id=chat_id,
        message=f'Условия ремонта одобрены клиентом, статус автоматически изменен на "в процессе".\n'
                f'Номер ремонта: {order_id}'
    )


def send_cancel_message(
        chat_id: int,
        order_id: int,
        message_sender: TelegramMessageSender = TelegramMessageSender
):
    session = sync_session_maker()
    session.execute(update(Order).where(Order.id == order_id).values({'status': Status.CANCELLED}))
    session.commit()
    session.close()

    message_sender.send_message(
        chat_id=chat_id,
        message=f'Клиент не согласился с условиями ремонта, статус автоматически изменен на "отменен".\n'
                f'Номер ремонта: {order_id}\n'
    )


green_api_bot.run_forever()
