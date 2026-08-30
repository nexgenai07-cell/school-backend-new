from rest_framework import serializers
from apps.users.models import Staff
from .models import Event, EventParticipation


class EventSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.user.name', read_only=True, default=None)
    # Custom field so a wrong ID type (e.g. admin's User ID instead of Staff ID)
    # returns an actionable message instead of DRF's cryptic "Invalid pk" 400.
    organizer = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.all(),
        required=False,
        allow_null=True,
        error_messages={
            'does_not_exist': 'organizer must be a valid Staff ID (from the staff table), '
                              'not a User ID — id "{pk_value}" was not found in staff. '
                              'Leave organizer empty if not applicable.',
        },
    )

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate_organizer(self, value):
        if value is not None:
            # 'organizer' references users.Staff — a common mistake is sending
            # the admin's User ID (users.User table), which yields a confusing
            # "Invalid pk" 400. Give a clear, actionable error instead.
            if not Staff.objects.filter(pk=value.pk).exists():
                raise serializers.ValidationError(
                    "organizer must be a Staff ID (from the staff table), "
                    "not a User ID. Leave organizer empty if not applicable, "
                    "or use the staff profile ID of the event organizer."
                )
        return value


class EventParticipationSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)
    student_name = serializers.CharField(source='student.user.name', read_only=True)

    class Meta:
        model = EventParticipation
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate(self, data):
        event = data.get('event') or getattr(self.instance, 'event', None)
        student = data.get('student') or getattr(self.instance, 'student', None)

        # Existing check: max_participants
        if event and event.max_participants:
            current_count = EventParticipation.objects.filter(event=event).exclude(
                id=getattr(self.instance, 'id', None)
            ).count()
            if current_count >= event.max_participants:
                raise serializers.ValidationError(
                    f"Event '{event.name}' has reached max participants ({event.max_participants})."
                )

        # NEW: same student, same event -> duplicate registration block
        if event and student:
            duplicate = EventParticipation.objects.filter(event=event, student=student).exclude(
                id=getattr(self.instance, 'id', None)
            )
            if duplicate.exists():
                raise serializers.ValidationError(
                    f"{student} is already registered for '{event.name}'."
                )

        return data