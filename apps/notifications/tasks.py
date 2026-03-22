from celery import shared_task
from .models import Notification


@shared_task
def send_notification(notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)

        print(f"Sending {notification.notification_type} to user {notification.user.username}")

        # simulate sending
        notification.status = 'SENT'
        notification.save()

        return "Success"

    except Notification.DoesNotExist:
        return "Notification not found"