from django.contrib import admin
from .models import Event, Notification, NotificationLog, IdempotencyKey


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "user", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = ("user__username", "event_type", "event")
    ordering = ("-created_at",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "event",
        "notification_type",
        "status",
        "retry_count",
        "created_at",
        "sent_at",
    )

    list_filter = ("status", "notification_type", "created_at")
    search_fields = ("user__username", "message")
    ordering = ("-created_at",)

    readonly_fields = ("created_at", "sent_at")

    # Inline logs inside notification (VERY USEFUL)
    class NotificationLogInline(admin.TabularInline):
        model = NotificationLog
        extra = 0
        readonly_fields = ("status", "response", "created_at")

    inlines = [NotificationLogInline]


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("id", "notification", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("notification__id",)
    ordering = ("-created_at",)

@admin.register(IdempotencyKey)
class IdempotencyKeyAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "created_at")
    search_fields = ("key",)
    ordering = ("-created_at",)