from apps.common.models import BaseModel
from django.db import models


class Class(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    academic_year = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'classes'

    def __str__(self):
        return self.name


class Section(BaseModel):
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=10)
    capacity = models.IntegerField(default=0)

    class Meta:
        db_table = 'sections'

    def __str__(self):
        return f"{self.class_obj.name} - {self.name}"


class Subject(BaseModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'subjects'

    def __str__(self):
        return self.name


class Room(BaseModel):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=100, blank=True)
    capacity = models.IntegerField(default=0)

    class Meta:
        db_table = 'rooms'

    def __str__(self):
        return self.name


class ClassSubject(BaseModel):
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_subjects')
    teacher = models.ForeignKey('users.Teacher', on_delete=models.SET_NULL, null=True, related_name='class_subjects')

    class Meta:
        db_table = 'class_subjects'
        # ✅ Prevents duplicate: same class + same subject + same teacher
        unique_together = ['class_obj', 'subject', 'teacher']

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

    def __str__(self):
        return f"{self.class_obj.name} - {self.subject.name} ({self.day})"