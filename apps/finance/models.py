from apps.common.models import BaseModel
from django.db import models


class FeeStructure(BaseModel):
    FREQUENCY_CHOICES = [('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')]

    class_obj = models.ForeignKey('academics.Class', on_delete=models.CASCADE, related_name='fee_structures')
    title = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'fee_structures'

    def __str__(self):
        return f"{self.class_obj.name} - {self.title}"


class Expense(BaseModel):
    PAYMENT_METHOD_CHOICES = [('cash', 'Cash'), ('bank', 'Bank'), ('online', 'Online')]

    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    paid_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='expenses_paid')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    class Meta:
        db_table = 'expenses'

    def __str__(self):
        return f"{self.category} - {self.amount}"


class Fee(BaseModel):
    STATUS_CHOICES = [('pending', 'Pending'), ('paid', 'Paid'), ('partial', 'Partial'), ('overdue', 'Overdue')]

    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='fees')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='fees')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'fees'

    def __str__(self):
        return f"{self.student} - {self.fee_structure.title}"


class Payment(BaseModel):
    PAYMENT_METHOD_CHOICES = [('cash', 'Cash'), ('bank', 'Bank'), ('online', 'Online')]

    fee = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True)
    receipt_no = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'payments'

    def save(self, *args, **kwargs):
        from django.core.exceptions import ValidationError

        total_paid = Payment.objects.filter(fee=self.fee).exclude(id=self.id).aggregate(
            total=models.Sum('amount_paid')
        )['total'] or 0
        new_total = total_paid + self.amount_paid

        if new_total > self.fee.amount:
            raise ValidationError(
                f"Payment exceeds fee amount. Fee: {self.fee.amount}, already paid: {total_paid}, "
                f"max allowed now: {self.fee.amount - total_paid}"
            )

        old_status = self.fee.status
        if new_total >= self.fee.amount:
            new_status = 'paid'
        elif new_total > 0:
            new_status = 'partial'
        else:
            new_status = 'pending'

        super().save(*args, **kwargs)

        if old_status != new_status:
            self.fee.status = new_status
            self.fee.save(update_fields=['status'])
            FeeHistory.objects.create(
                fee=self.fee,
                old_status=old_status,
                new_status=new_status,
                old_amount=self.fee.amount,
                new_amount=self.fee.amount,
                reason=f"Payment of {self.amount_paid} recorded",
            )

    def __str__(self):
        return f"{self.fee} - {self.amount_paid}"
class FeeHistory(BaseModel):
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name='history')
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    old_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    new_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='fee_changes')
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)

    class Meta:
        db_table = 'fee_history'

    def __str__(self):
        return f"{self.fee} - {self.old_status} -> {self.new_status}"
