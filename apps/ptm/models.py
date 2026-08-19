from apps.common.models import BaseModel
from django.db import models


class PTM(BaseModel):
    class_obj = models.ForeignKey('academics.Class', on_delete=models.CASCADE, related_name='ptm_events')
    name = models.CharField(max_length=150)
    date = models.DateField()
    type = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'ptm'

    def __str__(self):
        return self.name


class PTMMeeting(BaseModel):
    STATUS_CHOICES = [('scheduled', 'Scheduled'), ('completed', 'Completed')]

    ptm = models.ForeignKey(PTM, on_delete=models.CASCADE, related_name='meetings')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='ptm_meetings')
    teacher = models.ForeignKey('users.Teacher', on_delete=models.CASCADE, related_name='ptm_meetings')
    meeting_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    parent_feedback = models.TextField(blank=True)
    action_plan = models.TextField(blank=True)

    class Meta:
        db_table = 'ptm_meetings'
        # ✅ Database level constraint: Same teacher + same date + same time = unique
        unique_together = ['teacher', 'meeting_date', 'start_time', 'end_time']

    def __str__(self):
        return f"{self.ptm.name} - {self.student}"

class PTMAttendee(BaseModel):
    ptm_meeting = models.ForeignKey(PTMMeeting, on_delete=models.CASCADE, related_name='attendees')
    parent = models.ForeignKey('users.Parent', on_delete=models.CASCADE, related_name='ptm_attendances')
    attended = models.BooleanField(default=False)
    joined_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ptm_attendees'

    def __str__(self):
        return f"{self.ptm_meeting} - {self.parent}"
