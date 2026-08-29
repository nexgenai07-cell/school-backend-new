from rest_framework import serializers
from .models import DocumentType, Document


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class DocumentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    doc_type_name = serializers.CharField(source='doc_type.name', read_only=True, default=None)
    uploaded_by_name = serializers.CharField(source='uploaded_by.name', read_only=True, default=None)

    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate(self, data):
        request = self.context.get('request')
        user = data.get('user') or getattr(self.instance, 'user', None)
        doc_type = data.get('doc_type') or getattr(self.instance, 'doc_type', None)

        # Ownership check — sirf apne against, ya (parent) apne bacche ke against upload kar sake
        if request and request.user.role != 'admin' and user is not None:
            if user == request.user:
                allowed = True
            elif request.user.role == 'parent':
                student_profile = getattr(user, 'student_profile', None)
                allowed = student_profile is not None and student_profile.parent.user_id == request.user.id
            else:
                allowed = False
            if not allowed:
                raise serializers.ValidationError(
                    "You can only upload documents for yourself (or your child, if you are a parent)."
                )

        # Duplicate check — same user + same doc_type dobara na ho
        if user and doc_type:
            duplicate = Document.objects.filter(user=user, doc_type=doc_type).exclude(
                id=getattr(self.instance, 'id', None)
            )
            if duplicate.exists():
                raise serializers.ValidationError(
                    f"A document of type '{doc_type.name}' already exists for this user. "
                    f"Update the existing record instead of creating a duplicate."
                )

        return data