from rest_framework import viewsets
from rest_framework.exceptions import NotFound, PermissionDenied


class TenantModelViewSet(viewsets.ModelViewSet):
    """Applies tenant isolation to list, detail, create and update operations."""

    def get_tenant(self):
        tenant = getattr(self.request, "tenant", None)
        if tenant is None:
            raise NotFound("A valid tenant domain or X-Tenant-Slug header is required.")
        user = self.request.user
        if user.is_authenticated and not user.is_superuser and getattr(user, "school_id", None) != tenant.id:
            raise PermissionDenied("You do not belong to this school.")
        return tenant

    def filter_queryset(self, queryset):
        queryset = queryset.filter(school=self.get_tenant())
        return super().filter_queryset(queryset)

    def get_serializer_class(self):
        serializer_class = super().get_serializer_class()
        from apps.common.serializers import TenantModelSerializer
        if issubclass(serializer_class, TenantModelSerializer):
            return serializer_class
        # Existing serializers keep their public fields and custom validation;
        # this mixin adds the tenant relation validation centrally.
        return type(
            f"Tenant{serializer_class.__name__}",
            (TenantModelSerializer, serializer_class),
            {},
        )

    def perform_create(self, serializer):
        serializer.save(school=self.get_tenant())

    def perform_update(self, serializer):
        serializer.save(school=self.get_tenant())
