from rest_framework import serializers
from .models import GradeScale, Exam, Question, StudentAnswer, Result, AIAutoChecking

from django.utils import timezone
class GradeScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeScale
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']





class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    # ✅ Duplicate check
    def validate(self, data):
        class_obj = data.get('class_obj')
        subject = data.get('subject')
        exam_type = data.get('exam_type')
        
        # Check if combination already exists
        if Exam.objects.filter(
            class_obj=class_obj,
            subject=subject,
            exam_type=exam_type
        ).exists():
            # If updating, exclude current instance
            if self.instance:
                if Exam.objects.filter(
                    class_obj=class_obj,
                    subject=subject,
                    exam_type=exam_type
                ).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError(
                        f"Exam already exists for {class_obj.name} - {subject.name} ({exam_type})"
                    )
            else:
                raise serializers.ValidationError(
                    f"Exam already exists for {class_obj.name} - {subject.name} ({exam_type})"
                )
        
        return data


class QuestionSerializer(serializers.ModelSerializer):
    # ✅ Add these two fields
    class_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    # ✅ Get class name from exam
    def get_class_name(self, obj):
        if obj.exam and obj.exam.class_obj:
            return obj.exam.class_obj.name
        return None

    # ✅ Get subject name from exam
    def get_subject_name(self, obj):
        if obj.exam and obj.exam.subject:
            return obj.exam.subject.name
        return None

    def validate(self, data):
        exam = data.get('exam') or getattr(self.instance, 'exam', None)
        marks = data.get('marks', 0)

        existing_total = Question.objects.filter(exam=exam).exclude(
            id=getattr(self.instance, 'id', None)
        ).aggregate(total=serializers.models.Sum('marks'))['total'] or 0

        if existing_total + marks > exam.total_marks:
            raise serializers.ValidationError(
                f"Total question marks ({existing_total + marks}) would exceed exam total_marks ({exam.total_marks})."
            )
        return data




class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted', 'is_correct', 'marks_awarded']

    def validate(self, data):
        exam = data.get('exam') or getattr(self.instance, 'exam', None)

        # Sirf CREATE ke waqt date check karein (update/PATCH pe nahi, taake teacher/admin baad mein bhi is_correct set kar sakein)
        if self.instance is None:  # matlab yeh naya create ho raha hai
            if exam and exam.date < timezone.now().date():
                raise serializers.ValidationError(
                    "This exam has already passed. Answers cannot be submitted after the exam date."
                )
        return data

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted', 'percentage', 'grade', 'gpa']

    def validate(self, data):
        exam = data.get('exam') or getattr(self.instance, 'exam', None)
        marks = data.get('marks_obtained')
        if marks is not None and marks > exam.total_marks:
            raise serializers.ValidationError(
                f"marks_obtained ({marks}) cannot exceed exam total_marks ({exam.total_marks})."
            )
        if marks is not None and marks < 0:
            raise serializers.ValidationError("marks_obtained cannot be negative.")
        return data


class AIAutoCheckingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAutoChecking
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']