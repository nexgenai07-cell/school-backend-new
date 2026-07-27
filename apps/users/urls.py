from rest_framework.routers import DefaultRouter
from .views import UserViewSet, StudentViewSet, TeacherViewSet, StaffViewSet, ParentViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('students', StudentViewSet, basename='students')
router.register('teachers', TeacherViewSet, basename='teachers')
router.register('staff', StaffViewSet, basename='staff')
router.register('parents', ParentViewSet, basename='parents')

urlpatterns = router.urls
