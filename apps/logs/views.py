from rest_framework import viewsets
from apps.common.permissions import AuditLogPermission
from .models import ActivityLog, LoginLog, ErrorLog
from .serializers import ActivityLogSerializer, LoginLogSerializer, ErrorLogSerializer


class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [AuditLogPermission]


class LoginLogViewSet(viewsets.ModelViewSet):
    queryset = LoginLog.objects.all()
    serializer_class = LoginLogSerializer
    permission_classes = [AuditLogPermission]


class ErrorLogViewSet(viewsets.ModelViewSet):
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
    permission_classes = [AuditLogPermission]