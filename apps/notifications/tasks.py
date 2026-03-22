from celery import shared_task
from .models import Notification, NotificationLog
from django.utils import timezone


@shared_task(bind=True)
def send_notification(self, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)

        print(f"Sending {notification.notification_type} to user {notification.user.username}")

        # simulate success
        notification.status = 'SENT'
        notification.sent_at = timezone.now()
        notification.save()

        # ✅ create success log
        NotificationLog.objects.create(
            notification=notification,
            status='SUCCESS',
            response="Notification sent successfully"
        )

        return "Success"

    except Exception as e:
        # ❌ mark failed
        notification.status = 'FAILED'
        notification.retry_count += 1
        notification.save()

        # ❌ create failure log
        NotificationLog.objects.create(
            notification=notification,
            status='FAILED',
            response=str(e)
        )

        return "Failed"