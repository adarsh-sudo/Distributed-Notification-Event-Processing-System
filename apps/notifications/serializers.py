from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'user', 'event_type', 'data', 'created_at']

    def validate_event_type(self, value):
        allowed = ['ORDER_PLACED', 'PAYMENT_FAILED', 'MESSAGE_RECEIVED']
        if value not in allowed:
            raise serializers.ValidationError("Invalid event type")
        return value