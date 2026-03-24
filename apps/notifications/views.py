from rest_framework.response import Response
from rest_framework import status, generics
from django.db import transaction
from .utils import is_rate_limited
from .models import IdempotencyKey
from .services import process_event
from .serializers import EventSerializer


class EventCreateAPIView(generics.CreateAPIView):
    serializer_class = EventSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user")

        if is_rate_limited(user_id):
            return Response(
                {"error": "Rate limit exceeded"},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        idempotency_key = request.data.get("idempotency_key")

        if not idempotency_key:
            return Response(
                {"error": "idempotency_key is required"},
                status=400
            )

        # atomic transaction
        with transaction.atomic():

            key_obj, created = IdempotencyKey.objects.get_or_create(
                key=idempotency_key
            )

            # ✅ CASE 1: Already processed → return saved response
            if not created and key_obj.response_data:
                return Response(
                    key_obj.response_data,
                    status=key_obj.status_code
                )

            #  CASE 2: In progress (optional)
            if key_obj.is_processing:
                return Response(
                    {"message": "Request is already being processed"},
                    status=409
                )

            key_obj.is_processing = True
            key_obj.save()

            #  Process normally
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            event = serializer.save()
            notification = process_event(event)

            response_data = {
                "message": "Event processed",
                "event_id": event.id,
                "notification_id": notification.id
            }

            #  Save response
            key_obj.response_data = response_data
            key_obj.status_code = status.HTTP_201_CREATED
            key_obj.is_processing = False
            key_obj.save()

            return Response(response_data, status=201)