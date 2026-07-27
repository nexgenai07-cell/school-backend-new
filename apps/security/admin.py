from django.contrib import admin
from .models import Visitor, AccessLog, EntryExitLog

admin.site.register(Visitor)
admin.site.register(AccessLog)
admin.site.register(EntryExitLog)
