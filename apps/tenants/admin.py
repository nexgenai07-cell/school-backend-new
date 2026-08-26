from django.contrib import admin
from .models import School, Feature, SchoolFeature


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "domain", "is_active")
    search_fields = ("name", "slug", "domain")


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "default_enabled")
    search_fields = ("key", "name")
    list_filter = ("default_enabled",)


@admin.register(SchoolFeature)
class SchoolFeatureAdmin(admin.ModelAdmin):
    list_display = ("school", "feature", "is_enabled")
    list_filter = ("is_enabled", "feature")
    search_fields = ("school__name", "school__slug", "feature__key")
