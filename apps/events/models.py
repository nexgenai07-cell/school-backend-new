from apps.common.models import BaseModel
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import MinValueValidator
from django.db import models

class Event(BaseModel):
    EVENT_TYPE_CHOICES = [('academic', 'Academic'), ('sports', 'Sports'), ('other', 'Other')]

    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    event_date = models.DateField()
    description = models.TextField(blank=True)
    organizer = models.ForeignKey('users.Staff', on_delete=models.SET_NULL, null=True, related_name='organized_events')
    location = models.CharField(max_length=150, blank=True)
    max_participants = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1)],
        help_text="Leave blank for unlimited",
    )

    class Meta:
        db_table = 'events'

    def __str__(self):
        return self.name



class EventParticipation(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='event_participations')

    class Meta:
        db_table = 'event_participation'
        # A student can register for a given event only once.
        unique_together = ['event', 'student']

    def clean(self):
        if self.event_id and self.event.max_participants:
            current_count = EventParticipation.objects.filter(event_id=self.event_id).exclude(pk=self.pk).count()
            if current_count >= self.event.max_participants:
                raise DjangoValidationError(
                    f"Event '{self.event.name}' has reached max participants ({self.event.max_participants})."
                )

        if self.event_id and self.student_id:
            duplicate = EventParticipation.objects.filter(
                event_id=self.event_id, student_id=self.student_id
            ).exclude(pk=self.pk)
            if duplicate.exists():
                raise DjangoValidationError(f"This student is already registered for this event.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.event.name}"