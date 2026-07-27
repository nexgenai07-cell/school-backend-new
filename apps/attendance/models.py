from apps.common.models import BaseModel
from django.db import models


class Attendance(BaseModel):
    STATUS_CHOICES = [('present', 'Present'), ('absent', 'Absent'), ('late', 'Late')]

    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='attendance_records')
    teacher = models.ForeignKey('users.Teacher', on_delete=models.SET_NULL, null=True, related_name='attendance_marked')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey('users.Teacher', on_delete=models.SET_NULL, null=True, related_name='attendance_marked_by')

    class Meta:
        db_table = 'attendance'
        unique_together = ['student', 'date']   # <-- ADDED

    def __str__(self):
        return f"{self.student} - {self.date}"

class BehaviorLog(BaseModel):
    TYPE_CHOICES = [('positive', 'Positive'), ('negative', 'Negative')]
    SEVERITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]

    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='behavior_logs')
    teacher = models.ForeignKey('users.Teacher', on_delete=models.SET_NULL, null=True, related_name='behavior_logs')
    date = models.DateField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    action_taken = models.TextField(blank=True)

    class Meta:
        db_table = 'behavior_logs'

    def __str__(self):
        return f"{self.student} - {self.type}"
