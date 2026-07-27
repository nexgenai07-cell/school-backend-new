from django.contrib import admin
from .models import FeeStructure, Expense, Fee, Payment, FeeHistory

admin.site.register(FeeStructure)
admin.site.register(Expense)
admin.site.register(Fee)
admin.site.register(Payment)
admin.site.register(FeeHistory)
