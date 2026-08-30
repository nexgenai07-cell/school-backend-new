from apps.common.models import BaseModel
from django.db import models


class DocumentType(BaseModel):
    name = models.CharField(max_length=100, help_text="e.g. certificate/NIC/letter")
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'document_types'

    def __str__(self):
        return self.name


class Document(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='documents')
    doc_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, related_name='documents')
    file = models.FileField(
    upload_to="documents/",
    null=True,
    blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='documents_uploaded')

    class Meta:
        db_table = 'documents'
        # One document of a given type per user.
        unique_together = ['user', 'doc_type']

    def __str__(self):
        return f"{self.user} - {self.doc_type}"
