from rest_framework.routers import DefaultRouter
from .views import AttendanceViewSet, BehaviorLogViewSet

router = DefaultRouter()
router.register('attendance', AttendanceViewSet, basename='attendance')
router.register('behavior-logs', BehaviorLogViewSet, basename='behavior-logs')

urlpatterns = router.urls
