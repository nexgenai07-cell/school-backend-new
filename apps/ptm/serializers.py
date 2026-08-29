from rest_framework import serializers
from .models import PTM, PTMMeeting, PTMAttendee


class PTMSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_obj.name', read_only=True)

    class Meta:
        model = PTM
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class PTMMeetingSerializer(serializers.ModelSerializer):
    ptm_name = serializers.CharField(source='ptm.name', read_only=True)
    student_name = serializers.CharField(source='student.user.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.name', read_only=True)

    class Meta:
        model = PTMMeeting
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate(self, data):
        teacher = data.get('teacher') or getattr(self.instance, 'teacher', None)
        meeting_date = data.get('meeting_date') or getattr(self.instance, 'meeting_date', None)
        start_time = data.get('start_time') or getattr(self.instance, 'start_time', None)
        end_time = data.get('end_time') or getattr(self.instance, 'end_time', None)

        # ✅ Validation 1: Teacher already has a meeting at this time
        teacher_clashes = PTMMeeting.objects.filter(
            teacher=teacher,
            meeting_date=meeting_date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
        if self.instance:
            teacher_clashes = teacher_clashes.exclude(id=self.instance.id)
        if teacher_clashes.exists():
            raise serializers.ValidationError(
                f"Teacher {teacher.user.name} already has a meeting at this time."
            )

        # ✅ Validation 2: Student already has a meeting at this time
        student = data.get('student') or getattr(self.instance, 'student', None)
        student_clashes = PTMMeeting.objects.filter(
            student=student,
            meeting_date=meeting_date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
        if self.instance:
            student_clashes = student_clashes.exclude(id=self.instance.id)
        if student_clashes.exists():
            raise serializers.ValidationError(
                f"Student {student.user.name} already has a meeting at this time."
            )

        # ✅ Validation 3: End time must be after start time
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError(
                "End time must be after start time."
            )

        # ✅ Validation 4: Same teacher + same student + same date + same time
        exact_duplicate = PTMMeeting.objects.filter(
            teacher=teacher,
            student=student,
            meeting_date=meeting_date,
            start_time=start_time,
            end_time=end_time,
        )
        if self.instance:
            exact_duplicate = exact_duplicate.exclude(id=self.instance.id)
        if exact_duplicate.exists():
            raise serializers.ValidationError(
                f"A meeting for {student.user.name} with {teacher.user.name} already exists at this time."
            )

        return data


class PTMAttendeeSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.user.name', read_only=True)
    meeting_label = serializers.SerializerMethodField()

    class Meta:
        model = PTMAttendee
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def get_meeting_label(self, obj):
        return f"{obj.ptm_meeting.ptm.name} - {obj.ptm_meeting.student.user.name}"