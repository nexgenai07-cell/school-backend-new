from rest_framework import viewsets
from apps.common.permissions import ReadOnlyOrAdmin, IsAssignedTeacherOrAdmin, IsOwnerParentOrAdmin
from apps.users.models import Student, Teacher, Parent
from .models import GradeScale, Exam, Question, StudentAnswer, Result, AIAutoChecking
from .serializers import (
    GradeScaleSerializer, ExamSerializer, QuestionSerializer,
    StudentAnswerSerializer, ResultSerializer, AIAutoCheckingSerializer,
)


class GradeScaleViewSet(viewsets.ModelViewSet):
    queryset = GradeScale.objects.all()
    serializer_class = GradeScaleSerializer
    permission_classes = [ReadOnlyOrAdmin]


class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = [IsAssignedTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab exams
        if user.role == 'admin':
            return Exam.objects.all()
        
        # Teacher -> apne exams
        if user.role == 'teacher':
            return Exam.objects.filter(teacher__user=user)
        
        # Student -> apni class ki exams
        if user.role == 'student':
            return Exam.objects.filter(class_obj__students__user=user)
        
        # Parent -> bachchon ki class ki exams
        if user.role == 'parent':
            return Exam.objects.filter(class_obj__students__parent__user=user)
        
        return Exam.objects.none()


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [IsAssignedTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab questions
        if user.role == 'admin':
            return Question.objects.all()
        
        # Teacher -> apne exams ke questions
        if user.role == 'teacher':
            return Question.objects.filter(exam__teacher__user=user)
        
        # Student -> apni class ke exams ke questions (only after exam date)
        # ⚠️ Security: Students shouldn't see questions before exam
        if user.role == 'student':
            from django.utils import timezone
            return Question.objects.filter(
                exam__class_obj__students__user=user,
                exam__date__lte=timezone.now().date()
            )
        
        # Parent -> bachchon ki class ke exams ke questions (only after exam date)
        if user.role == 'parent':
            from django.utils import timezone
            return Question.objects.filter(
                exam__class_obj__students__parent__user=user,
                exam__date__lte=timezone.now().date()
            )
        
        return Question.objects.none()


class StudentAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = StudentAnswerSerializer
    permission_classes = [IsOwnerParentOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab answers
        if user.role == 'admin':
            return StudentAnswer.objects.all()
        
        # Teacher -> sirf apne students ke answers
        if user.role == 'teacher':
            return StudentAnswer.objects.filter(
                student__class_obj__class_subjects__teacher__user=user
            ).distinct()
        
        # Student -> apne answers
        if user.role == 'student':
            return StudentAnswer.objects.filter(student__user=user)
        
        # Parent -> bachchon ke answers
        if user.role == 'parent':
            return StudentAnswer.objects.filter(student__parent__user=user)
        
        return StudentAnswer.objects.none()


class ResultViewSet(viewsets.ModelViewSet):
    serializer_class = ResultSerializer
    permission_classes = [IsOwnerParentOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab results
        if user.role == 'admin':
            return Result.objects.all()
        
        # Teacher -> sirf apne exams ke results
        if user.role == 'teacher':
            return Result.objects.filter(exam__teacher__user=user)
        
        # Student -> apne results
        if user.role == 'student':
            return Result.objects.filter(student__user=user)
        
        # Parent -> bachchon ke results
        if user.role == 'parent':
            return Result.objects.filter(student__parent__user=user)
        
        return Result.objects.none()


class AIAutoCheckingViewSet(viewsets.ModelViewSet):
    serializer_class = AIAutoCheckingSerializer
    permission_classes = [IsOwnerParentOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab AI checks
        if user.role == 'admin':
            return AIAutoChecking.objects.all()
        
        # Teacher -> sirf apne exams ke AI checks
        if user.role == 'teacher':
            return AIAutoChecking.objects.filter(exam__teacher__user=user)
        
        # Student -> apne AI checks
        if user.role == 'student':
            return AIAutoChecking.objects.filter(student__user=user)
        
        # Parent -> bachchon ke AI checks
        if user.role == 'parent':
            return AIAutoChecking.objects.filter(student__parent__user=user)
        
        return AIAutoChecking.objects.none()