from django.contrib import admin
from .models import Bus, Route, BusStop, BusStudent, TransportAttendance

admin.site.register(Bus)
admin.site.register(Route)
admin.site.register(BusStop)
admin.site.register(BusStudent)
admin.site.register(TransportAttendance)
