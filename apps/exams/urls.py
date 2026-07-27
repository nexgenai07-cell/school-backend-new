from rest_framework.routers import DefaultRouter
from .views import (
    GradeScaleViewSet, ExamViewSet, QuestionViewSet,
    StudentAnswerViewSet, ResultViewSet, AIAutoCheckingViewSet,
)

router = DefaultRouter()
router.register('grade-scale', GradeScaleViewSet, basename='grade-scale')
router.register('exams', ExamViewSet, basename='exams')
router.register('questions', QuestionViewSet, basename='questions')
router.register('student-answers', StudentAnswerViewSet, basename='student-answers')
router.register('results', ResultViewSet, basename='results')
router.register('ai-auto-checking', AIAutoCheckingViewSet, basename='ai-auto-checking')

urlpatterns = router.urls
