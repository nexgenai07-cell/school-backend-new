from rest_framework import viewsets
from apps.common.permissions import IsSenderOrReceiverOrAdmin, IsOwnerOrAdmin, NotificationLogPermission
from .models import Message, Notification, NotificationLog
from .serializers import MessageSerializer, NotificationSerializer, NotificationLogSerializer


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsSenderOrReceiverOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Message.objects.all()
        from django.db.models import Q
        return Message.objects.filter(Q(sender=user) | Q(receiver=user))


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Notification.objects.all()
        return Notification.objects.filter(user=user)


class NotificationLogViewSet(viewsets.ModelViewSet):
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer
    permission_classes = [NotificationLogPermission]