from django.contrib import admin
from .models import Book, BookIssue, BookIssueHistory

admin.site.register(Book)
admin.site.register(BookIssue)
admin.site.register(BookIssueHistory)
