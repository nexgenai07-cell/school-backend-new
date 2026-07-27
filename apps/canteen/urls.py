from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, MenuItemViewSet, OrderItemViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('menu-items', MenuItemViewSet, basename='menu-items')
router.register('order-items', OrderItemViewSet, basename='order-items')

urlpatterns = router.urls
