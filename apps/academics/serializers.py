from rest_framework import serializers
from .models import Class, Section, Subject, Room, ClassSubject, Timetable


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class SectionSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_obj.name', read_only=True)

    class Meta:
        model = Section
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class ClassSubjectSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(
        source='teacher.user.name', read_only=True, default=None
    )

    class Meta:
        model = ClassSubject
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class TimetableSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True, default=None)

    class Meta:
        model = Timetable
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate(self, data):
        room = data.get('room') or getattr(self.instance, 'room', None)
        teacher = data.get('teacher') or getattr(self.instance, 'teacher', None)
        day = data.get('day') or getattr(self.instance, 'day', None)
        start_time = data.get('start_time') or getattr(self.instance, 'start_time', None)
        end_time = data.get('end_time') or getattr(self.instance, 'end_time', None)

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("start_time must be before end_time.")

        # Check 1: Same room, same day, overlapping time -> clash
        if room:
            room_clashes = Timetable.objects.filter(
                room=room, day=day,
                start_time__lt=end_time, end_time__gt=start_time,
            )
            if self.instance:
                room_clashes = room_clashes.exclude(id=self.instance.id)
            if room_clashes.exists():
                raise serializers.ValidationError(
                    f"Room '{room.name}' is already booked for another class at this time on {day}."
                )

        # Check 2: Same teacher, same day, overlapping time -> clash
        if teacher:
            teacher_clashes = Timetable.objects.filter(
                teacher=teacher, day=day,
                start_time__lt=end_time, end_time__gt=start_time,
            )
            if self.instance:
                teacher_clashes = teacher_clashes.exclude(id=self.instance.id)
            if teacher_clashes.exists():
                raise serializers.ValidationError(
                    f"Teacher is already assigned to another class at this time on {day}."
                )

        return data
