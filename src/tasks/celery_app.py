from datetime import datetime, timedelta

from celery import Celery, shared_task
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from config import settings
from database import sync_session_maker
from models import Order, Status
from services.message_sender import WhatsAppMessageSender

celery_app: Celery = Celery(
    'tasks',
    broker=f'{settings.REDIS_URL}/2',
    broker_connection_retry_on_startup=True,
    celery_broker_connection_retry=True,
    celery_result_backend=f'{settings.REDIS_URL}/2'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    worker_hijack_root_logger=False,
)

celery_app.autodiscover_tasks()


@shared_task
def send_notification(message_sender: WhatsAppMessageSender = WhatsAppMessageSender):
    with sync_session_maker() as session:
        orders = session.scalars(
            select(Order)
            .filter_by(status=Status.COMPLETED)
            .options(joinedload(Order.client))
        )

        for order in orders:
            if datetime.utcnow() - order.last_notif_at >= timedelta(minutes=1):
                message_sender.sync_send_message(
                    number=order.client.phone,
                    message=f'Уважаемый {order.client.name},\n'
                            f'Ваш инструмент можно забрать ежедневно с 08:00 до 20:00.'
                )
                session.execute(update(Order).where(Order.id == order.id).values({'last_notif_at': datetime.utcnow()}))

        session.commit()


celery_app.conf.beat_schedule = {
    'send_notifications': {
        'task': 'tasks.celery_app.send_notification',
        'schedule': timedelta(minutes=1)
    },
}
