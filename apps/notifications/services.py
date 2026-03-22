from .models import Event, Notification
from .tasks import send_notification
import logging
logger = logging.getLogger(__name__)

def process_event(event: Event):
    """
    Handles event → notification → async trigger
    """
    logger.info(f"Processing event {event.id} of type {event.event_type} for user {event.user_id}")
    # 1. Create Notification
    existing = Notification.objects.filter(event=event).first()

    if existing:
        return existing
    
    notification = Notification.objects.create(
        user=event.user,
        event=event,
        notification_type='EMAIL',
        message=f"{event.event_type} triggered"
    )

    # 2. Trigger async task
    send_notification.delay(notification.id)

    return notification