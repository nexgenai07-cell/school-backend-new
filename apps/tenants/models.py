from django.db import models
from django.utils.text import slugify


class School(models.Model):
    """The data-isolation boundary for a school using this platform."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=80)
    domain = models.CharField(max_length=255, unique=True, null=True, blank=True)
    database_alias = models.CharField(
        max_length=50,
        default='default',
        help_text="Django DATABASES alias where this school's rows live. "
                  "'default' = shared Neon; other values = dedicated shards.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def has_feature(self, key):
        """True if this school has the given feature enabled.

        Resolution order: explicit SchoolFeature override first, then the
        Feature's default_enabled, else False for unknown features.
        """
        override = self.feature_overrides.filter(feature__key=key).first()
        if override is not None:
            return override.is_enabled
        feature = Feature.objects.filter(key=key).first()
        return feature.default_enabled if feature else False


class Feature(models.Model):
    """Platform-level feature registry. One row per togglable capability."""

    key = models.SlugField(unique=True, max_length=100)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    default_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "features"
        ordering = ["key"]

    def __str__(self):
        return self.name


class SchoolFeature(models.Model):
    """Per-school override for a feature. Absence of a row means 'use default'."""

    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="feature_overrides"
    )
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    is_enabled = models.BooleanField()

    class Meta:
        db_table = "school_features"
        unique_together = ["school", "feature"]

    def __str__(self):
        state = "enabled" if self.is_enabled else "disabled"
        return f"{self.school.slug}: {self.feature.key} ({state})"

