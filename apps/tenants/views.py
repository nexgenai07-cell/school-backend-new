from rest_framework import permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import School
from .serializers import SchoolSerializer


class IsPlatformAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsPlatformAdmin]


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def current_tenant(request):
    if request.tenant is None:
        return Response({"detail": "A valid tenant domain or X-Tenant-Slug header is required."}, status=400)
    if getattr(request.user, "school_id", None) != request.tenant.id and not request.user.is_superuser:
        return Response({"detail": "You do not belong to this school."}, status=403)
    return Response(SchoolSerializer(request.tenant).data)
