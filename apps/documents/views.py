from rest_framework import viewsets
from apps.common.permissions import ReadOnlyOrAdmin, DocumentsPermission
from django.db.models import Q
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

        if user.role == 'teacher':
            return Document.objects.filter(
                Q(user=user) |
                Q(user__student_profile__class_obj__class_subjects__teacher__user=user)
            ).distinct()

        if user.role == 'staff':
            return Document.objects.filter(
                Q(user=user) | Q(user__student_profile__isnull=False)
            ).distinct()

        if user.role == 'parent':
            return Document.objects.filter(
                Q(user=user) | Q(user__student_profile__parent__user=user)
            )

        # student (and any other role) -> only their own
        return Document.objects.filter(user=user)