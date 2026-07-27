from rest_framework import serializers
from .models import Event, EventParticipation


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class EventParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventParticipation
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate(self, data):
        event = data.get('event') or getattr(self.instance, 'event', None)
        if event and event.max_participants:
            current_count = EventParticipation.objects.filter(event=event).exclude(
                id=getattr(self.instance, 'id', None)
            ).count()
            if current_count >= event.max_participants:
                raise serializers.ValidationError(f"Event '{event.name}' has reached max participants ({event.max_participants}).")
        return data