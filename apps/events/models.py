from apps.common.models import BaseModel
from django.db import models


class Event(BaseModel):
    EVENT_TYPE_CHOICES = [('academic', 'Academic'), ('sports', 'Sports'), ('other', 'Other')]

    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    event_date = models.DateField()
    description = models.TextField(blank=True)
    organizer = models.ForeignKey('users.Staff', on_delete=models.SET_NULL, null=True, related_name='organized_events')
    location = models.CharField(max_length=150, blank=True)
    max_participants = models.IntegerField(null=True, blank=True, help_text="Leave blank for unlimited")   # <-- NEW FIELD

    class Meta:
        db_table = 'events'

    def __str__(self):
        return self.name

class EventParticipation(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='event_participations')

    class Meta:
        db_table = 'event_participation'

    def __str__(self):
        return f"{self.student} - {self.event.name}"
