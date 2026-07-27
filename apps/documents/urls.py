from rest_framework.routers import DefaultRouter
from .views import DocumentTypeViewSet, DocumentViewSet

router = DefaultRouter()
router.register('document-types', DocumentTypeViewSet, basename='document-types')
router.register('documents', DocumentViewSet, basename='documents')

urlpatterns = router.urls
