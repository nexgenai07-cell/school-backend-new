from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """Default manager — hides soft-deleted rows."""
    def get_queryset(self):
        queryset = super().get_queryset().filter(is_deleted=False)
        # Import lazily so model loading does not create an app-registry cycle.
        from apps.tenants.context import current_tenant
        tenant = current_tenant.get()
        if tenant is not None:
            queryset = queryset.filter(school=tenant)
        return queryset


class BaseModel(models.Model):
    """
    Abstract base model — extend this in every app's models.py.
    Gives every table: created_at, updated_at, is_active, soft-delete.
    """
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    school = models.ForeignKey(
        'tenants.School', on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_records',
        db_index=True, editable=False, null=True, blank=True,
    )

    objects = SoftDeleteManager()   # default queryset -> deleted rows hidden
    all_objects = models.Manager()  # full queryset, for admin/audit

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def delete(self, using=None, keep_parents=False, hard=False):
        if hard:
            return super().delete(using=using, keep_parents=keep_parents)
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def save(self, *args, **kwargs):
        """Bind writes to the request tenant and reject cross-tenant writes."""
        from django.core.exceptions import ValidationError
        from apps.tenants.context import current_tenant

        tenant = current_tenant.get()
        if tenant is not None:
            if self.school_id and self.school_id != tenant.id:
                raise ValidationError('Cross-tenant writes are not allowed.')
            self.school = tenant
        super().save(*args, **kwargs)

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])
