from apps.common.models import BaseModel
from django.db import models


class ActivityLog(BaseModel):
    """Global audit trail -- receives writes from every module."""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='activity_logs', help_text="Who performed the action")
    action = models.CharField(max_length=50, help_text="create/update/delete etc")
    entity_type = models.CharField(max_length=100, help_text="Table name e.g. 'students'")
    entity_id = models.IntegerField(help_text="Row ID affected")
    old_data = models.JSONField(null=True, blank=True, help_text="Before state")
    new_data = models.JSONField(null=True, blank=True, help_text="After state")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_logs'

    def __str__(self):
        return f"{self.user} - {self.action} - {self.entity_type}"


class LoginLog(BaseModel):
    STATUS_CHOICES = [('success', 'Success'), ('failed', 'Failed')]

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='login_logs')
    login_time = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        db_table = 'login_logs'

    def __str__(self):
        return f"{self.user} - {self.status}"


class ErrorLog(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='error_logs', help_text="Null if system error")
    error_type = models.CharField(max_length=150)
    error_message = models.TextField()
    url = models.CharField(max_length=255, blank=True, help_text="Where it occurred")
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'error_logs'

    def __str__(self):
        return f"{self.error_type} - {self.created_at}"
