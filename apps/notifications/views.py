from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from .models import Event, Notification
from .serializers import EventSerializer
from .tasks import send_notification


class EventCreateAPIView(CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # 1. Save Event
            event = serializer.save()

            # 2. Create Notification
            notification = Notification.objects.create(
                user=event.user,
                event=event,
                notification_type='EMAIL',
                message=f"{event.event_type} triggered"
            )

            # 3. Send Async Task
            send_notification.delay(notification.id)

            return Response(
                {
                    "message": "Event created and notification queued",
                    "event_id": event.id,
                    "notification_id": notification.id
                },
                status=status.HTTP_201_CREATED
            )