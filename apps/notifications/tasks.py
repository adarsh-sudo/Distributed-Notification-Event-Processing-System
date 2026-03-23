from celery import shared_task
from .models import Notification, NotificationLog
from django.utils import timezone

PERMANENT_ERRORS = (
    ValueError,                 # invalid data
    TypeError,                  # coding/data issue
    Notification.DoesNotExist,  # wrong ID
    PermissionError,            # no access
)
TEMPORARY_ERRORS = (
    ConnectionError,        # network issue
    TimeoutError,           # request timeout
    OSError,                # system/network glitch
)
@shared_task(bind=True, max_retries=5)
def send_notification(self, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        return "Notification not found"
    
    try:
        print(f"Sending {notification.notification_type} to user {notification.user.username}")
    
        if notification.status == 'SENT':
            return "Already processed"
        import random

        # #  simulate different failures
        # rand = random.choice(["success", "temp", "perm"])

        # if rand == "temp":
        #     raise ConnectionError("Temporary network issue")
        # elif rand == "perm":
        #     raise ValueError("Invalid email address")
        # simulate success
        notification.status = 'SENT'
        notification.sent_at = timezone.now()
        notification.save()

        #  create success log
        NotificationLog.objects.create(
            notification=notification,
            status='SUCCESS',
            response="Notification sent successfully"
        )

        return "Success"

    except Exception as e:

                #  PERMANENT FAILURE
        if isinstance(e, PERMANENT_ERRORS):
            notification.status = 'FAILED'
            notification.failure_reason = str(e)
            notification.save()

            NotificationLog.objects.create(
                notification=notification,
                status='FAILED',
                response=f"Permanent failure: {str(e)}"
            )

            return "Permanent Failure"

        #  TEMPORARY FAILURE → RETRY
        elif isinstance(e, TEMPORARY_ERRORS):
            notification.retry_count += 1
            notification.save()

            NotificationLog.objects.create(
                notification=notification,
                status='FAILED',
                response=f"Retry {notification.retry_count}: {str(e)}"
            )

            raise self.retry(
                exc=e,
                countdown=2 ** self.request.retries
            )

        #  UNKNOWN FAILURE
        else:
            notification.status = 'FAILED'
            notification.failure_reason = str(e)
            notification.save()

            NotificationLog.objects.create(
                notification=notification,
                status='FAILED',
                response=f"Unknown error: {str(e)}"
            )

            return "Unknown Failure"