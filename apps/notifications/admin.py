from django.contrib import admin
from .models import Event, Notification
from .models import NotificationLog

admin.site.register(NotificationLog)
admin.site.register(Event)
admin.site.register(Notification)