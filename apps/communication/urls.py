from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, NotificationViewSet, NotificationLogViewSet

router = DefaultRouter()
router.register('messages', MessageViewSet, basename='messages')
router.register('notifications', NotificationViewSet, basename='notifications')
router.register('notification-log', NotificationLogViewSet, basename='notification-log')

urlpatterns = router.urls
