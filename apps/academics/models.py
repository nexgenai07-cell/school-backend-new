from apps.common.models import BaseModel
from django.db import models

from django.core.exceptions import ValidationError as DjangoValidationError

class Class(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    academic_year = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'classes'
        # Same school cannot define the same class twice in one academic year.
        unique_together = ['school', 'name', 'academic_year']

    def __str__(self):
        return self.name


class Section(BaseModel):
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=10)
    capacity = models.IntegerField(default=0)

    class Meta:
        db_table = 'sections'
        # Same class cannot have two sections with the same name (e.g. two "A").
        unique_together = ['class_obj', 'name']

    def __str__(self):
        return f"{self.class_obj.name} - {self.name}"


class Subject(BaseModel):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'subjects'
        # Per-school unique: School A and School B can each have "MATH".
        constraints = [
            models.UniqueConstraint(fields=['school', 'code'], name='uniq_subject_school_code'),
        ]

    def __str__(self):
        return self.name


class Room(BaseModel):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=100, blank=True)
    capacity = models.IntegerField(default=0)

    class Meta:
        db_table = 'rooms'
        unique_together = ['school', 'name']

    def __str__(self):
        return self.name


class ClassSubject(BaseModel):
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_subjects')
    teacher = models.ForeignKey('users.Teacher', on_delete=models.SET_NULL, null=True, related_name='class_subjects')

    class Meta:
        db_table = 'class_subjects'
        constraints = [
            # same class + same subject + same teacher can exist only once
            models.UniqueConstraint(
                fields=['class_obj', 'subject', 'teacher'],
                name='uniq_classsubject_teacher',
            ),
            # teacher is nullable: Postgres treats NULLs as distinct, so also
            # enforce uniqueness on (class_obj, subject) when teacher is NULL.
            models.UniqueConstraint(
                fields=['class_obj', 'subject'],
                condition=models.Q(teacher__isnull=True),
                name='uniq_classsubject_no_teacher',
            ),
        ]

    def __str__(self):
        return f"{self.class_obj.name} - {self.subject.name}"


class Timetable(BaseModel):
    DAY_CHOICES = [
        ('mon', 'Monday'), ('tue', 'Tuesday'), ('wed', 'Wednesday'),
        ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'), ('sun', 'Sunday'),
    ]

    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='timetable_slots')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='timetable_slots')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetable_slots')
    teacher = models.ForeignKey('users.Teacher', on_delete=models.CASCADE, related_name='timetable_slots')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, related_name='timetable_slots')
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = 'timetable'

    def clean(self):
        if self.section_id and self.class_obj_id and self.section.class_obj_id != self.class_obj_id:
            raise DjangoValidationError("Selected section does not belong to this class.")

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise DjangoValidationError("start_time must be before end_time.")

        if self.room_id and self.day and self.start_time and self.end_time:
            room_clashes = Timetable.objects.filter(
                room_id=self.room_id, day=self.day,
                start_time__lt=self.end_time, end_time__gt=self.start_time,
            )
            if self.pk:
                room_clashes = room_clashes.exclude(pk=self.pk)
            if room_clashes.exists():
                raise DjangoValidationError(
                    f"This room is already booked for another class at this time on {self.day}."
                )

        if self.teacher_id and self.day and self.start_time and self.end_time:
            teacher_clashes = Timetable.objects.filter(
                teacher_id=self.teacher_id, day=self.day,
                start_time__lt=self.end_time, end_time__gt=self.start_time,
            )
            if self.pk:
                teacher_clashes = teacher_clashes.exclude(pk=self.pk)
            if teacher_clashes.exists():
                raise DjangoValidationError(
                    "This teacher is already assigned to another class at this time on this day."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.class_obj.name} - {self.subject.name} ({self.day})"