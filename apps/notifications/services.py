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
    notification, created = Notification.objects.get_or_create(
    event=event,
    defaults={
        "user": event.user,
        "notification_type": "EMAIL",
        "message": f"{event.event_type} triggered"
            }
        )

    if created:
        send_notification.delay(notification.id)

    return notification