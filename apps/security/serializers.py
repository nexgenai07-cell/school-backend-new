from rest_framework import serializers
from .models import Visitor, AccessLog, EntryExitLog


class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class AccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class EntryExitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryExitLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate(self, data):
        student = data.get('student') or getattr(self.instance, 'student', None)
        entry_time = data.get('entry_time') or getattr(self.instance, 'entry_time', None)
        exit_time = data.get('exit_time', None) if 'exit_time' in data else getattr(self.instance, 'exit_time', None)

        # Check 1: Same student, same entry_time — exact duplicate
        if student and entry_time:
            duplicate = EntryExitLog.objects.filter(student=student, entry_time=entry_time)
            if self.instance:
                duplicate = duplicate.exclude(id=self.instance.id)
            if duplicate.exists():
                raise serializers.ValidationError(
                    f"An entry log for {student} at this exact time already exists."
                )

        # Check 2: Student can't have a new "open" entry (no exit yet) while another is still open
        if student and not self.instance and exit_time is None:
            open_entry = EntryExitLog.objects.filter(student=student, exit_time__isnull=True)
            if open_entry.exists():
                raise serializers.ValidationError(
                    f"{student} already has an open entry (no exit recorded yet). "
                    f"Record the exit before adding a new entry."
                )

        return data