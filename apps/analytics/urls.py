from rest_framework.routers import DefaultRouter
from .views import (
    SkillMappingViewSet, AutomationRuleViewSet, AutomationLogViewSet,
    AnalyticsSnapshotViewSet, PredictionViewSet, RecommendationViewSet,
    StudentGoalViewSet, StudentSkillViewSet, ParentEngagementViewSet,
)

router = DefaultRouter()
router.register('skill-mapping', SkillMappingViewSet, basename='skill-mapping')
router.register('automation-rules', AutomationRuleViewSet, basename='automation-rules')
router.register('automation-logs', AutomationLogViewSet, basename='automation-logs')
router.register('snapshots', AnalyticsSnapshotViewSet, basename='snapshots')
router.register('predictions', PredictionViewSet, basename='predictions')
router.register('recommendations', RecommendationViewSet, basename='recommendations')
router.register('student-goals', StudentGoalViewSet, basename='student-goals')
router.register('student-skills', StudentSkillViewSet, basename='student-skills')
router.register('parent-engagement', ParentEngagementViewSet, basename='parent-engagement')

urlpatterns = router.urls
