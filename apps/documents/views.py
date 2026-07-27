from rest_framework import viewsets
from apps.common.permissions import ReadOnlyOrAdmin, DocumentsPermission
from .models import DocumentType, Document
from .serializers import DocumentTypeSerializer, DocumentSerializer


class DocumentTypeViewSet(viewsets.ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer
    permission_classes = [ReadOnlyOrAdmin]


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [DocumentsPermission]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Document.objects.all()
        if user.role == 'parent':
            from django.db.models import Q
            return Document.objects.filter(
                Q(user=user) | Q(user__student_profile__parent__user=user)
            )
        return Document.objects.filter(user=user)