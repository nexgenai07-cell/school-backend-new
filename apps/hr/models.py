from apps.common.models import BaseModel
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Department(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'departments'
        unique_together = ['school', 'name']

    def __str__(self):
        return self.name


class Employee(BaseModel):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='employee_profile')
    designation = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    join_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    leave_balance = models.IntegerField(default=20, validators=[MinValueValidator(0)], help_text="Remaining annual leave days")   # <-- NEW FIELD

    class Meta:
        db_table = 'employees'

    def save(self, *args, **kwargs):
        if self.pk:
            old = Employee.objects.filter(pk=self.pk).first()
            if old and old.salary != self.salary:
                super().save(*args, **kwargs)
                SalaryHistory.objects.create(
                    employee=self, old_salary=old.salary, new_salary=self.salary, reason="Salary updated",
                )
                return
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.name

class Payroll(BaseModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_records')
    month = models.CharField(max_length=20)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True)
    paid_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'payroll'
        # One payroll per employee per month.
        unique_together = ['employee', 'month']

    def save(self, *args, **kwargs):
        self.net_salary = self.basic_salary + self.allowances - self.deductions
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.user.name} - {self.month}"

class Leave(BaseModel):
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'leaves'

    def save(self, *args, **kwargs):
        from django.core.exceptions import ValidationError

        old_status = None
        if self.pk:
            old = Leave.objects.filter(pk=self.pk).first()
            old_status = old.status if old else None

        requested_days = (self.end_date - self.start_date).days + 1

        if old_status != 'approved' and self.status == 'approved':
            if requested_days > self.employee.leave_balance:
                raise ValidationError(
                    f"Insufficient leave balance. Requested: {requested_days}, available: {self.employee.leave_balance}"
                )
            self.employee.leave_balance -= requested_days
            self.employee.save(update_fields=['leave_balance'])

        super().save(*args, **kwargs)

        if old_status is not None and old_status != self.status:
            LeaveHistory.objects.create(
                leave=self, status_old=old_status, status_new=self.status,
                reason=f"Status changed from {old_status} to {self.status}",
            )

    def __str__(self):
        return f"{self.employee.user.name} - {self.leave_type}"

class SalaryHistory(BaseModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_history')
    old_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    new_salary = models.DecimalField(max_digits=12, decimal_places=2)
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='salary_changes')
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)

    class Meta:
        db_table = 'salary_history'

    def __str__(self):
        return f"{self.employee.user.name} - {self.new_salary}"


class LeaveHistory(BaseModel):
    leave = models.ForeignKey(Leave, on_delete=models.CASCADE, related_name='history')
    status_old = models.CharField(max_length=20, blank=True)
    status_new = models.CharField(max_length=20, blank=True)
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='leave_changes')
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)

    class Meta:
        db_table = 'leave_history'

    def __str__(self):
        return f"{self.leave} - {self.status_old} -> {self.status_new}"
