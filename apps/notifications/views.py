from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from .models import Event
from .serializers import EventSerializer
from .services import process_event


class EventCreateAPIView(CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # 1. Save Event
            event = serializer.save()

            # 2. Create Notification
            notification = process_event(event)

            return Response(
                {
                    "message": "Event created and notification queued",
                    "event_id": event.id,
                    "notification_id": notification.id
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)