from rest_framework.routers import DefaultRouter
from .views import (
    BusViewSet, RouteViewSet, BusStopViewSet,
    BusStudentViewSet, TransportAttendanceViewSet,
)

router = DefaultRouter()
router.register('buses', BusViewSet, basename='buses')
router.register('routes', RouteViewSet, basename='routes')
router.register('bus-stops', BusStopViewSet, basename='bus-stops')
router.register('bus-students', BusStudentViewSet, basename='bus-students')
router.register('transport-attendance', TransportAttendanceViewSet, basename='transport-attendance')

urlpatterns = router.urls
