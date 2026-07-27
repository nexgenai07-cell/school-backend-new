from rest_framework import serializers
from .models import PTM, PTMMeeting, PTMAttendee


class PTMSerializer(serializers.ModelSerializer):
    class Meta:
        model = PTM
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class PTMMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PTMMeeting
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate(self, data):
        teacher = data.get('teacher') or getattr(self.instance, 'teacher', None)
        meeting_date = data.get('meeting_date') or getattr(self.instance, 'meeting_date', None)
        start_time = data.get('start_time') or getattr(self.instance, 'start_time', None)
        end_time = data.get('end_time') or getattr(self.instance, 'end_time', None)

        clashes = PTMMeeting.objects.filter(
            teacher=teacher, meeting_date=meeting_date,
            start_time__lt=end_time, end_time__gt=start_time,
        )
        if self.instance:
            clashes = clashes.exclude(id=self.instance.id)
        if clashes.exists():
            raise serializers.ValidationError("Teacher already has a meeting at this time.")
        return data

class PTMAttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PTMAttendee
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']
