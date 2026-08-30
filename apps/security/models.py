from apps.common.models import BaseModel
from django.db import models
# apps/security/models.py mein EntryExitLog class update karein
from django.core.exceptions import ValidationError as DjangoValidationError

class Visitor(BaseModel):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    purpose = models.CharField(max_length=255, blank=True)
    in_time = models.DateTimeField(null=True, blank=True)
    out_time = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey('users.Staff', on_delete=models.SET_NULL, null=True, related_name='approved_visitors')

    class Meta:
        db_table = 'visitors'

    def clean(self):
        if self.in_time and self.out_time and self.out_time < self.in_time:
            raise DjangoValidationError("out_time cannot be before in_time.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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
        # DB-level: the same student cannot have two entries at the exact same time.
        unique_together = ['student', 'entry_time']

    def clean(self):
        if self.entry_time and self.exit_time and self.exit_time < self.entry_time:
            raise DjangoValidationError("exit_time cannot be before entry_time.")

        if self.student_id and self.entry_time:
            duplicate = EntryExitLog.objects.filter(
                student_id=self.student_id, entry_time=self.entry_time
            ).exclude(pk=self.pk)
            if duplicate.exists():
                raise DjangoValidationError("An entry log for this student at this exact time already exists.")

        if self.student_id and not self.pk and self.exit_time is None:
            open_entry = EntryExitLog.objects.filter(student_id=self.student_id, exit_time__isnull=True)
            if open_entry.exists():
                raise DjangoValidationError(
                    "This student already has an open entry (no exit recorded yet)."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} entry/exit"