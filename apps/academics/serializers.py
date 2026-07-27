from rest_framework import serializers
from .models import Class, Section, Subject, Room, ClassSubject, Timetable


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class SectionSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = ClassSubject
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']
