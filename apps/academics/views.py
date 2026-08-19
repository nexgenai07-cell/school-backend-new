from rest_framework import viewsets
from apps.common.permissions import ReadOnlyOrAdmin, IsAssignedTeacherOrAdmin
from .models import Class, Section, Subject, Room, ClassSubject, Timetable
from .serializers import (
    ClassSerializer, SectionSerializer, SubjectSerializer,
    RoomSerializer, ClassSubjectSerializer, TimetableSerializer,
)


class ClassViewSet(viewsets.ModelViewSet):
    serializer_class = ClassSerializer
    permission_classes = [ReadOnlyOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Class.objects.all()
        if user.role == 'teacher':
            return Class.objects.filter(class_subjects__teacher__user=user).distinct()
        if user.role == 'student':
            return Class.objects.filter(students__user=user)
        if user.role == 'parent':
            return Class.objects.filter(students__parent__user=user).distinct()
        return Class.objects.none()


class SectionViewSet(viewsets.ModelViewSet):
    serializer_class = SectionSerializer
    permission_classes = [ReadOnlyOrAdmin]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            queryset = Section.objects.all()
        elif user.role == 'teacher':
            queryset = Section.objects.filter(class_obj__class_subjects__teacher__user=user).distinct()
        elif user.role == 'student':
            queryset = Section.objects.filter(class_obj__students__user=user)
        elif user.role == 'parent':
            queryset = Section.objects.filter(class_obj__students__parent__user=user).distinct()
        else:
            queryset = Section.objects.none()

        # React frontend ke liye — Class select karne pe uski sections filter karne ka support
        class_id = self.request.query_params.get('class_obj')
        if class_id:
            queryset = queryset.filter(class_obj_id=class_id)

        return queryset

class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    permission_classes = [ReadOnlyOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Subject.objects.all()
        if user.role == 'teacher':
            return Subject.objects.filter(class_subjects__teacher__user=user).distinct()
        if user.role == 'student':
            return Subject.objects.filter(class_subjects__class_obj__students__user=user).distinct()
        if user.role == 'parent':
            return Subject.objects.filter(class_subjects__class_obj__students__parent__user=user).distinct()
        return Subject.objects.none()


class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [ReadOnlyOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Room.objects.all()
        if user.role == 'teacher':
            return Room.objects.filter(timetable_slots__teacher__user=user).distinct()
        if user.role == 'student':
            return Room.objects.filter(timetable_slots__class_obj__students__user=user).distinct()
        if user.role == 'parent':
            return Room.objects.filter(timetable_slots__class_obj__students__parent__user=user).distinct()
        return Room.objects.none()

class ClassSubjectViewSet(viewsets.ModelViewSet):
    serializer_class = ClassSubjectSerializer
    permission_classes = [IsAssignedTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return ClassSubject.objects.all()
        if user.role == 'teacher':
            return ClassSubject.objects.filter(teacher__user=user).distinct()
        if user.role == 'student':
            return ClassSubject.objects.filter(class_obj__students__user=user).distinct()
        if user.role == 'parent':
            return ClassSubject.objects.filter(class_obj__students__parent__user=user).distinct()
        return ClassSubject.objects.none()


class TimetableViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableSerializer
    permission_classes = [IsAssignedTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Timetable.objects.all()
        if user.role == 'teacher':
            return Timetable.objects.filter(teacher__user=user)
        if user.role == 'student':
            return Timetable.objects.filter(class_obj__students__user=user)
        if user.role == 'parent':
            return Timetable.objects.filter(class_obj__students__parent__user=user)
        return Timetable.objects.none()