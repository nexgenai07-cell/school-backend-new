from rest_framework.routers import DefaultRouter
from .views import ActivityLogViewSet, LoginLogViewSet, ErrorLogViewSet

router = DefaultRouter()
router.register('activity-logs', ActivityLogViewSet, basename='activity-logs')
router.register('login-logs', LoginLogViewSet, basename='login-logs')
router.register('error-logs', ErrorLogViewSet, basename='error-logs')

urlpatterns = router.urls
