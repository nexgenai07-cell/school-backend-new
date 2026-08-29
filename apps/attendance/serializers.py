from rest_framework import serializers
from .models import Attendance, BehaviorLog


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.name', read_only=True, default=None)
    marked_by_name = serializers.CharField(source='marked_by.user.name', read_only=True, default=None)

    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate(self, data):
        student = data.get('student') or getattr(self.instance, 'student', None)
        date = data.get('date') or getattr(self.instance, 'date', None)
        qs = Attendance.objects.filter(student=student, date=date)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Attendance already marked for this student on this date.")
        return data


class BehaviorLogSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.name', read_only=True, default=None)

    class Meta:
        model = BehaviorLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']