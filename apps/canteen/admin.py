from django.contrib import admin
from .models import Category, MenuItem, OrderItem

admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(OrderItem)
