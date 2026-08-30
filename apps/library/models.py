from apps.common.models import BaseModel
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

class Book(BaseModel):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150, blank=True)
    isbn = models.CharField(max_length=30)
    category = models.ForeignKey('canteen.Category', on_delete=models.SET_NULL, null=True, related_name='books')
    description = models.TextField(blank=True)
    total_copies = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    available_copies = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'books'
        # Two schools can legitimately own the same book (same ISBN).
        constraints = [
            models.UniqueConstraint(fields=['school', 'isbn'], name='uniq_book_school_isbn'),
        ]

    def clean(self):
        if self.available_copies > self.total_copies:
            raise DjangoValidationError("available_copies cannot exceed total_copies.")

    def __str__(self):
        return self.title


class BookIssue(BaseModel):
    STATUS_CHOICES = [('issued', 'Issued'), ('returned', 'Returned'), ('overdue', 'Overdue')]
    FINE_PER_DAY = 10

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='book_issues')
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    fine = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')

    class Meta:
        db_table = 'book_issues'

    def save(self, *args, **kwargs):
        from django.core.exceptions import ValidationError

        is_new = self.pk is None
        old_status = None

        if is_new:
            if self.book.available_copies <= 0:
                raise ValidationError(f"No copies of '{self.book.title}' available.")
            self.book.available_copies -= 1
            self.book.save(update_fields=['available_copies'])
        else:
            old = BookIssue.objects.get(pk=self.pk)
            old_status = old.status

        if self.return_date:
            self.status = 'returned'
            if self.return_date > self.due_date:
                overdue_days = (self.return_date - self.due_date).days
                self.fine = overdue_days * self.FINE_PER_DAY
            if old_status and old_status != 'returned':
                self.book.available_copies += 1
                self.book.save(update_fields=['available_copies'])
        elif self.due_date < timezone.now().date() and self.status == 'issued':
            self.status = 'overdue'

        super().save(*args, **kwargs)

        if old_status is not None and old_status != self.status:
            BookIssueHistory.objects.create(
                book_issue=self,
                status_old=old_status,
                status_new=self.status,
                reason=f"Status changed from {old_status} to {self.status}",
            )

    def __str__(self):
        return f"{self.student} - {self.book.title}"
class BookIssueHistory(BaseModel):
    book_issue = models.ForeignKey(BookIssue, on_delete=models.CASCADE, related_name='history')
    status_old = models.CharField(max_length=20, blank=True)
    status_new = models.CharField(max_length=20, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='book_issue_changes')
    reason = models.TextField(blank=True)

    class Meta:
        db_table = 'book_issue_history'

    def __str__(self):
        return f"{self.book_issue} - {self.status_old} -> {self.status_new}"
