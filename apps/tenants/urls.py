from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SchoolViewSet, current_tenant

router = DefaultRouter()
router.register("schools", SchoolViewSet, basename="schools")

urlpatterns = [path("current/", current_tenant, name="current-tenant")] + router.urls
