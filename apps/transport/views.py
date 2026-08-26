from rest_framework import viewsets
from apps.common.views import TenantModelViewSet
from apps.common.permissions import TransportPermission
from apps.users.models import Student, Teacher, Parent
from .models import Bus, Route, BusStop, BusStudent, TransportAttendance
from .serializers import (
    BusSerializer, RouteSerializer, BusStopSerializer,
    BusStudentSerializer, TransportAttendanceSerializer,
)


class BusViewSet(TenantModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
    permission_classes = [TransportPermission]


class RouteViewSet(TenantModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [TransportPermission]


class BusStopViewSet(TenantModelViewSet):
    queryset = BusStop.objects.all()
    serializer_class = BusStopSerializer
    permission_classes = [TransportPermission]


class BusStudentViewSet(TenantModelViewSet):
    serializer_class = BusStudentSerializer
    permission_classes = [TransportPermission]

    def get_queryset(self):
        user = self.request.user
        
        # Admin, Staff -> sab
        if user.role in ['admin', 'staff']:
            return BusStudent.objects.all()
        
        # Teacher -> apne students ki bus assignments
        if user.role == 'teacher':
            return BusStudent.objects.filter(
                student__class_obj__class_subjects__teacher__user=user
            ).distinct()
        
        # Student -> apni bus assignment
        if user.role == 'student':
            return BusStudent.objects.filter(student__user=user)
        
        # Parent -> bachchon ki bus assignments
        if user.role == 'parent':
            return BusStudent.objects.filter(student__parent__user=user)
        
        return BusStudent.objects.none()


class TransportAttendanceViewSet(TenantModelViewSet):
    serializer_class = TransportAttendanceSerializer
    permission_classes = [TransportPermission]

    def get_queryset(self):
        user = self.request.user
        
        # Admin, Staff -> sab
        if user.role in ['admin', 'staff']:
            return TransportAttendance.objects.all()
        
        # Teacher -> apne students ki transport attendance
        if user.role == 'teacher':
            return TransportAttendance.objects.filter(
                bus_student__student__class_obj__class_subjects__teacher__user=user
            ).distinct()
        
        # Student -> apni transport attendance
        if user.role == 'student':
            return TransportAttendance.objects.filter(bus_student__student__user=user)
        
        # Parent -> bachchon ki transport attendance
        if user.role == 'parent':
            return TransportAttendance.objects.filter(bus_student__student__parent__user=user)
        
        return TransportAttendance.objects.none()