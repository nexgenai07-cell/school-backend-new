from django.contrib import admin
from .models import User, Student, Teacher, Staff, Parent

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Staff)
admin.site.register(Parent)