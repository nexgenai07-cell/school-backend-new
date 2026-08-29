from rest_framework import serializers
from .models import Assignment, Submission


class AssignmentSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.name', read_only=True, default=None)

    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate(self, data):
        request = self.context.get('request')
        teacher_user = request.user if request else None
        subject = data.get('subject') or getattr(self.instance, 'subject', None)
        class_obj = data.get('class_obj') or getattr(self.instance, 'class_obj', None)

        if teacher_user and teacher_user.role == 'teacher' and subject and class_obj:
            from apps.academics.models import ClassSubject
            is_assigned = ClassSubject.objects.filter(
                teacher__user=teacher_user, subject=subject, class_obj=class_obj
            ).exists()
            if not is_assigned:
                raise serializers.ValidationError(
                    f"You are not assigned to teach {subject} for this class."
                )
        return data

class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)

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