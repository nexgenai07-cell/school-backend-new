from rest_framework import serializers
from .models import GradeScale, Exam, Question, StudentAnswer, Result, AIAutoChecking


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
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


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