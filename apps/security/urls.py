from rest_framework.routers import DefaultRouter
from .views import VisitorViewSet, AccessLogViewSet, EntryExitLogViewSet

router = DefaultRouter()
router.register('visitors', VisitorViewSet, basename='visitors')
router.register('access-logs', AccessLogViewSet, basename='access-logs')
router.register('entry-exit-logs', EntryExitLogViewSet, basename='entry-exit-logs')

urlpatterns = router.urls
