from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

EVENT_TYPES = (
    ('ORDER_PLACED', 'Order Placed'),
    ('PAYMENT_FAILED', 'Payment Failed'),
    ('MESSAGE_RECEIVED', 'Message Received'),
)


class Event(models.Model):
    event = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=32, choices=EVENT_TYPES)
    data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if hasattr(self.user, 'username') else str(self.user)
        return f"{self.event_type}-{username}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('IN_APP', 'In App'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    failure_reason = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    retry_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.notification_type} - {self.status}"
    
    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['notification_type']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['event'],
                name='unique_notification_per_event'
            )
        ]


class NotificationLog(models.Model):
    STATUS_CHOICES = (
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )

    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="logs")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    response = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification.id} - {self.status}"
    

class IdempotencyKey(models.Model):
    key = models.CharField(max_length=255, unique=True)

    response_data = models.JSONField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)

    is_processing = models.BooleanField(default=False)  # 🔥 important
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.key