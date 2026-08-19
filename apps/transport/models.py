from apps.common.models import BaseModel
from django.db import models
from django.core.exceptions import ValidationError as DjangoValidationError

class Bus(BaseModel):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    bus_no = models.CharField(max_length=20, unique=True)
    capacity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        db_table = 'buses'

    def __str__(self):
        return self.bus_no


class Route(BaseModel):
    name = models.CharField(max_length=150, help_text="Route name")
    description = models.TextField(blank=True)
    start_point = models.CharField(max_length=150, blank=True)
    end_point = models.CharField(max_length=150, blank=True)

    class Meta:
        db_table = 'routes'

    def __str__(self):
        return self.name


class BusStop(BaseModel):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=150, help_text="Stop name")
    stop_order = models.IntegerField(help_text="Sequence")

    class Meta:
        db_table = 'bus_stops'
        ordering = ['stop_order']

    def __str__(self):
        return f"{self.route.name} - {self.name}"


# apps/transport/models.py mein BusStudent class update karein


class BusStudent(BaseModel):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='bus_students')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='bus_assignments')
    pickup_stop = models.ForeignKey(BusStop, on_delete=models.SET_NULL, null=True, related_name='pickups')
    drop_stop = models.ForeignKey(BusStop, on_delete=models.SET_NULL, null=True, related_name='drops')

    class Meta:
        db_table = 'bus_students'
        # ✅ Optional: Database level unique constraint
        unique_together = ['student']  # Ek student sirf ek bus

    def __str__(self):
        return f"{self.student} - {self.bus.bus_no}"
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='bus_students')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='bus_assignments')
    pickup_stop = models.ForeignKey(BusStop, on_delete=models.SET_NULL, null=True, related_name='pickups')
    drop_stop = models.ForeignKey(BusStop, on_delete=models.SET_NULL, null=True, related_name='drops')

    class Meta:
        db_table = 'bus_students'
        # ✅ Optional: Database level unique constraint
        unique_together = ['student']  # Ek student sirf ek bus

    def __str__(self):
        return f"{self.student} - {self.bus.bus_no}"
    """Bridges buses <-> students (M:N) with pickup & drop stop references."""
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='bus_students')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='bus_assignments')
    pickup_stop = models.ForeignKey(BusStop, on_delete=models.SET_NULL, null=True, related_name='pickups')
    drop_stop = models.ForeignKey(BusStop, on_delete=models.SET_NULL, null=True, related_name='drops')

    class Meta:
        db_table = 'bus_students'

    def clean(self):
        if self.bus_id:
            current_count = BusStudent.objects.filter(bus_id=self.bus_id).exclude(pk=self.pk).count()
            if current_count >= self.bus.capacity:
                raise DjangoValidationError(f"Bus {self.bus.bus_no} is at full capacity ({self.bus.capacity}).")

        if self.student_id:
            duplicate = BusStudent.objects.filter(student_id=self.student_id).exclude(pk=self.pk)
            if duplicate.exists():
                raise DjangoValidationError(
                    f"{self.student} is already assigned to a bus."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.bus.bus_no}"
class TransportAttendance(BaseModel):
    bus_student = models.ForeignKey(BusStudent, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    boarded = models.BooleanField(default=False)
    dropped = models.BooleanField(default=False)
    boarding_time = models.TimeField(null=True, blank=True)
    dropping_time = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = 'transport_attendance'

    def __str__(self):
        return f"{self.bus_student} - {self.date}"
