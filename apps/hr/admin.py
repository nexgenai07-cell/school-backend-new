from django.contrib import admin
from .models import Department, Employee, Leave, Payroll, SalaryHistory, LeaveHistory

admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(Leave)
admin.site.register(Payroll)
admin.site.register(SalaryHistory)
admin.site.register(LeaveHistory)
