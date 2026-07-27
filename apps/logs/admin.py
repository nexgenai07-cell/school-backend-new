from django.contrib import admin
from .models import ActivityLog, LoginLog, ErrorLog

admin.site.register(ActivityLog)
admin.site.register(LoginLog)
admin.site.register(ErrorLog)
