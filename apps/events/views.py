from rest_framework import viewsets
from apps.common.permissions import EventsPermission
from .models import Event, EventParticipation
from .serializers import EventSerializer, EventParticipationSerializer


class EventViewSet(viewsets.ModelViewSet):
    # ✅ FIX #2: Sab authenticated users ko sab events dikhein
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [EventsPermission]


class EventParticipationViewSet(viewsets.ModelViewSet):
    serializer_class = EventParticipationSerializer
    permission_classes = [EventsPermission]

    def get_queryset(self):
        user = self.request.user
        
        # Admin, Staff -> sab participations
        if user.role in ['admin', 'staff']:
            return EventParticipation.objects.all()
        
        # Teacher -> apne students ki participations
        if user.role == 'teacher':
            return EventParticipation.objects.filter(
                student__class_obj__class_subjects__teacher__user=user
            ).distinct()
        
        # Student -> apni participations
        if user.role == 'student':
            return EventParticipation.objects.filter(student__user=user)
        
        # Parent -> bachchon ki participations
        if user.role == 'parent':
            return EventParticipation.objects.filter(student__parent__user=user)
        
        return EventParticipation.objects.none()