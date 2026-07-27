from rest_framework.routers import DefaultRouter
from .views import EventViewSet, EventParticipationViewSet

router = DefaultRouter()
router.register('events', EventViewSet, basename='events')
router.register('event-participation', EventParticipationViewSet, basename='event-participation')

urlpatterns = router.urls
