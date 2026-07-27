from django.contrib import admin
from .models import GradeScale, Exam, Question, StudentAnswer, Result, AIAutoChecking

admin.site.register(GradeScale)
admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(StudentAnswer)
admin.site.register(Result)
admin.site.register(AIAutoChecking)
