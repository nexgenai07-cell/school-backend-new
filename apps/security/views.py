from rest_framework import viewsets
from apps.common.views import TenantModelViewSet
from apps.common.permissions import SecurityPermission
from .models import Visitor, AccessLog, EntryExitLog
from .serializers import VisitorSerializer, AccessLogSerializer, EntryExitLogSerializer


class VisitorViewSet(TenantModelViewSet):
    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer
    permission_classes = [SecurityPermission]


class AccessLogViewSet(TenantModelViewSet):
    queryset = AccessLog.objects.all()
    serializer_class = AccessLogSerializer
    permission_classes = [SecurityPermission]


class EntryExitLogViewSet(TenantModelViewSet):
    serializer_class = EntryExitLogSerializer
    permission_classes = [SecurityPermission]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'staff']:
            return EntryExitLog.objects.all()
        if user.role == 'parent':
            return EntryExitLog.objects.filter(student__parent__user=user)
        return EntryExitLog.objects.none()