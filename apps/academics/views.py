from rest_framework import viewsets
from apps.common.permissions import ReadOnlyOrAdmin, IsAssignedTeacherOrAdmin
from apps.users.models import Student, Teacher, Parent
from .models import Class, Section, Subject, Room, ClassSubject, Timetable
from .serializers import (
    ClassSerializer, SectionSerializer, SubjectSerializer,
    RoomSerializer, ClassSubjectSerializer, TimetableSerializer,
)


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [ReadOnlyOrAdmin]


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [ReadOnlyOrAdmin]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [ReadOnlyOrAdmin]


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [ReadOnlyOrAdmin]


class ClassSubjectViewSet(viewsets.ModelViewSet):
    serializer_class = ClassSubjectSerializer
    permission_classes = [IsAssignedTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab
        if user.role == 'admin':
            return ClassSubject.objects.all()
        
        # Teacher -> apne subjects
        if user.role == 'teacher':
            return ClassSubject.objects.filter(teacher__user=user).distinct()
        
        # Student -> apni class ke subjects
        if user.role == 'student':
            return ClassSubject.objects.filter(
                class_obj__students__user=user
            ).distinct()
        
        # Parent -> bachchon ki class ke subjects
        if user.role == 'parent':
            return ClassSubject.objects.filter(
                class_obj__students__parent__user=user
            ).distinct()
        
        return ClassSubject.objects.none()


class TimetableViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableSerializer
    permission_classes = [IsAssignedTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab
        if user.role == 'admin':
            return Timetable.objects.all()
        
        # Teacher -> apna timetable
        if user.role == 'teacher':
            return Timetable.objects.filter(teacher__user=user)
        
        # Student -> apna timetable
        if user.role == 'student':
            return Timetable.objects.filter(class_obj__students__user=user)
        
        # Parent -> bachchon ka timetable
        if user.role == 'parent':
            return Timetable.objects.filter(class_obj__students__parent__user=user)
        
        return Timetable.objects.none()