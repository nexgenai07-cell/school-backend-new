from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.users.views import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/tenants/', include('apps.tenants.urls')),
    path('custom-admin/', include('apps.common.admin_urls')),

    path('api/users/', include('apps.users.urls')),
    path('api/academics/', include('apps.academics.urls')),
    path('api/assignments/', include('apps.assignments.urls')),
    path('api/exams/', include('apps.exams.urls')),
    path('api/attendance/', include('apps.attendance.urls')),
    path('api/ptm/', include('apps.ptm.urls')),
    path('api/communication/', include('apps.communication.urls')),
    path('api/finance/', include('apps.finance.urls')),
    path('api/hr/', include('apps.hr.urls')),
    path('api/transport/', include('apps.transport.urls')),
    path('api/library/', include('apps.library.urls')),
    path('api/canteen/', include('apps.canteen.urls')),
    path('api/security/', include('apps.security.urls')),
    path('api/events/', include('apps.events.urls')),
    path('api/documents/', include('apps.documents.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/logs/', include('apps.logs.urls')),
]

from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
