from django.contrib import admin
from .models import Class, Section, Subject, Room, ClassSubject, Timetable

admin.site.register(Class)
admin.site.register(Section)
admin.site.register(Subject)
admin.site.register(Room)
admin.site.register(ClassSubject)
admin.site.register(Timetable)
