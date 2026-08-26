from django.http import JsonResponse
from .context import current_tenant
from .models import School


class TenantMiddleware:
    """Resolve the tenant before views run, without trusting a tenant id body field."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = self.get_tenant(request)
        # Django-admin requests use session authentication (already run by
        # AuthenticationMiddleware). A school admin is therefore confined to
        # their own school even when they did not supply a tenant header.
        if (
            request.tenant is None
            and request.path.startswith("/admin/")
            and getattr(request, "user", None)
            and request.user.is_authenticated
            and not request.user.is_superuser
        ):
            request.tenant = request.user.school
        token = current_tenant.set(request.tenant)
        try:
            # Tenant management is deliberately platform-admin only. Every
            # school-data endpoint requires an explicitly resolved tenant.
            if (
                request.path.startswith("/api/")
                and not request.path.startswith("/api/tenants/schools/")
                and request.tenant is None
            ):
                return JsonResponse(
                    {"detail": "A valid tenant domain or X-Tenant-Slug header is required."},
                    status=400,
                )
            return self.get_response(request)
        finally:
            current_tenant.reset(token)

    @staticmethod
    def get_tenant(request):
        # A custom domain takes precedence.  For local/API clients, use the
        # slug header; authorization is still enforced by TenantModelViewSet.
        host = request.get_host().split(":", 1)[0].lower()
        tenant = School.objects.filter(domain__iexact=host, is_active=True).first()
        if tenant:
            return tenant

        slug = request.headers.get("X-Tenant-Slug", "").strip().lower()
        if slug:
            return School.objects.filter(slug=slug, is_active=True).first()
        return None
