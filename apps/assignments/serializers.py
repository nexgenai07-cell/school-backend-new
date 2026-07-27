from rest_framework import serializers
from .models import Assignment, Submission


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate(self, data):
        assignment = data.get('assignment') or getattr(self.instance, 'assignment', None)
        marks = data.get('marks_obtained')
        if marks is not None and assignment and marks > assignment.total_marks:
            raise serializers.ValidationError(
                f"marks_obtained ({marks}) cannot exceed assignment total_marks ({assignment.total_marks})."
            )
        return data