from rest_framework.routers import DefaultRouter
from .views import (
    ClassViewSet, SectionViewSet, SubjectViewSet,
    RoomViewSet, ClassSubjectViewSet, TimetableViewSet,
)

router = DefaultRouter()
router.register('classes', ClassViewSet, basename='classes')
router.register('sections', SectionViewSet, basename='sections')
router.register('subjects', SubjectViewSet, basename='subjects')
router.register('rooms', RoomViewSet, basename='rooms')
router.register('class-subjects', ClassSubjectViewSet, basename='class-subjects')
router.register('timetable', TimetableViewSet, basename='timetable')

urlpatterns = router.urls
