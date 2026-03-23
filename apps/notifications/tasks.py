from celery import shared_task
from django.db import transaction
from django.utils import timezone
from .models import Notification, NotificationLog

PERMANENT_ERRORS = (
    ValueError,
    TypeError,
    Notification.DoesNotExist,
    PermissionError,
)

TEMPORARY_ERRORS = (
    ConnectionError,
    TimeoutError,
    OSError,
)

@shared_task(bind=True, max_retries=5)
def send_notification(self, notification_id):

    # STEP 1: Lock row + check status
    try:
        with transaction.atomic():
            notification = (
                Notification.objects
                .select_for_update()
                .get(id=notification_id)
            )

            #  Idempotency checks
            if notification.status == 'SENT':
                return "Already processed"

    except Notification.DoesNotExist:
        return "Notification not found"

    # STEP 2: Do actual work OUTSIDE lock
    try:
        print(f"Sending {notification.notification_type} to user {notification.user.username}")

        # import random
        # rand = random.choice(["temp"])

        # if rand == "temp":
        #     raise ConnectionError("Temporary network issue")
        # elif rand == "perm":
        #     raise ValueError("Invalid email address")

        # SUCCESS
        notification.status = 'SENT'
        notification.sent_at = timezone.now()
        notification.save()

        NotificationLog.objects.create(
            notification=notification,
            status='SUCCESS',
            response="Notification sent successfully"
        )

        return "Success"

    except Exception as e:

        # PERMANENT FAILURE
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

        # TEMPORARY FAILURE → RETRY
        elif isinstance(e, TEMPORARY_ERRORS):
            notification.retry_count = self.request.retries + 1
            notification.save()

            NotificationLog.objects.create(
                notification=notification,
                status='FAILED',
                response=f"Retry {notification.retry_count}: {str(e)}"
            )

            if self.request.retries >= self.max_retries:
                notification.status = 'FAILED'
                notification.failure_reason = "Max retries exceeded"
                notification.save()

                NotificationLog.objects.create(
                    notification=notification,
                    status='FAILED',
                    response="Max retries exceeded"
                )

                return "Final Failed"

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