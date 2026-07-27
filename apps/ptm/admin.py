from django.contrib import admin
from .models import PTM, PTMMeeting, PTMAttendee

admin.site.register(PTM)
admin.site.register(PTMMeeting)
admin.site.register(PTMAttendee)
