from rest_framework import viewsets
from apps.common.views import TenantModelViewSet
from apps.common.permissions import ReadOnlyOrAdmin, CanteenPermission, CanteenMenuPermission
from .models import Category, MenuItem, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, OrderItemSerializer


class CategoryViewSet(TenantModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrAdmin]
    permission_classes = [CanteenMenuPermission]  # staff/admin menu management


class MenuItemViewSet(TenantModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [ReadOnlyOrAdmin]
    permission_classes = [CanteenMenuPermission]  # staff/admin menu management


class OrderItemViewSet(TenantModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [CanteenPermission]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'staff']:
            return OrderItem.objects.all()
        if user.role == 'student':
            return OrderItem.objects.filter(student__user=user)
        if user.role == 'parent':
            return OrderItem.objects.filter(student__parent__user=user)
        return OrderItem.objects.none()