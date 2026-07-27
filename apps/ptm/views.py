from rest_framework import viewsets
from apps.common.permissions import PTMPermission
from apps.users.models import Student, Teacher, Parent
from .models import PTM, PTMMeeting, PTMAttendee
from .serializers import PTMSerializer, PTMMeetingSerializer, PTMAttendeeSerializer


class PTMViewSet(viewsets.ModelViewSet):
    serializer_class = PTMSerializer
    permission_classes = [PTMPermission]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab PTMs
        if user.role == 'admin':
            return PTM.objects.all()
        
        # Teacher -> sirf apni classes ki PTMs
        if user.role == 'teacher':
            return PTM.objects.filter(
                class_obj__class_subjects__teacher__user=user
            ).distinct()
        
        # Student -> apni class ki PTMs
        if user.role == 'student':
            return PTM.objects.filter(class_obj__students__user=user)
        
        # Parent -> bachchon ki class ki PTMs
        if user.role == 'parent':
            return PTM.objects.filter(class_obj__students__parent__user=user)
        
        return PTM.objects.none()


class PTMMeetingViewSet(viewsets.ModelViewSet):
    serializer_class = PTMMeetingSerializer
    permission_classes = [PTMPermission]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab meetings
        if user.role == 'admin':
            return PTMMeeting.objects.all()
        
        # Teacher -> apni meetings
        if user.role == 'teacher':
            return PTMMeeting.objects.filter(teacher__user=user)
        
        # Student -> apni meetings
        if user.role == 'student':
            return PTMMeeting.objects.filter(student__user=user)
        
        # Parent -> bachchon ki meetings
        if user.role == 'parent':
            return PTMMeeting.objects.filter(student__parent__user=user)
        
        return PTMMeeting.objects.none()


class PTMAttendeeViewSet(viewsets.ModelViewSet):
    serializer_class = PTMAttendeeSerializer
    permission_classes = [PTMPermission]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab attendees
        if user.role == 'admin':
            return PTMAttendee.objects.all()
        
        # Teacher -> apni meetings ke attendees
        if user.role == 'teacher':
            return PTMAttendee.objects.filter(ptm_meeting__teacher__user=user)
        
        # Parent -> apni attendance
        if user.role == 'parent':
            return PTMAttendee.objects.filter(parent__user=user)
        
        # Student -> apni meetings ke attendees
        if user.role == 'student':
            return PTMAttendee.objects.filter(ptm_meeting__student__user=user)
        
        return PTMAttendee.objects.none()