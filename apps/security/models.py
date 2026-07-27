from apps.common.models import BaseModel
from django.db import models


class Visitor(BaseModel):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    purpose = models.CharField(max_length=255, blank=True)
    in_time = models.DateTimeField(null=True, blank=True)
    out_time = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey('users.Staff', on_delete=models.SET_NULL, null=True, related_name='approved_visitors')

    class Meta:
        db_table = 'visitors'

    def __str__(self):
        return self.name


class AccessLog(BaseModel):
    VIA_CHOICES = [('web', 'Web'), ('mobile', 'Mobile'), ('app', 'App')]

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='access_logs')
    action = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device = models.CharField(max_length=150, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    via = models.CharField(max_length=20, choices=VIA_CHOICES)

    class Meta:
        db_table = 'access_logs'

    def __str__(self):
        return f"{self.user} - {self.action}"


class EntryExitLog(BaseModel):
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='entry_exit_logs')
    entry_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'entry_exit_logs'

    def __str__(self):
        return f"{self.student} entry/exit"
