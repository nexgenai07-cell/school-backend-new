from django.contrib import admin
from .models import Message, Notification, NotificationLog

admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(NotificationLog)
