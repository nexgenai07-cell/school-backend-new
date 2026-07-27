from rest_framework.routers import DefaultRouter
from .views import PTMViewSet, PTMMeetingViewSet, PTMAttendeeViewSet

router = DefaultRouter()
router.register('ptm', PTMViewSet, basename='ptm')
router.register('ptm-meetings', PTMMeetingViewSet, basename='ptm-meetings')
router.register('ptm-attendees', PTMAttendeeViewSet, basename='ptm-attendees')

urlpatterns = router.urls
