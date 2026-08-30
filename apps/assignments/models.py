from apps.common.models import BaseModel
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models


class Assignment(BaseModel):
    STATUS_CHOICES = [('active', 'Active'), ('closed', 'Closed')]

    class_obj = models.ForeignKey('academics.Class', on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey('users.Teacher', on_delete=models.SET_NULL, null=True, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    total_marks = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        db_table = 'assignments'

    def __str__(self):
        return self.title


class Submission(BaseModel):
    STATUS_CHOICES = [('submitted', 'Submitted'), ('late', 'Late')]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(
        upload_to="submissions/",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'zip']
        )],
    )
    submission_date = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')

    class Meta:
        db_table = 'submissions'
        # A student can submit a given assignment only once.
        unique_together = ['assignment', 'student']

    def clean(self):
        from django.core.exceptions import ValidationError as DjangoValidationError
        if self.file and self.file.size > 5 * 1024 * 1024:
            raise DjangoValidationError("Submission file cannot exceed 5 MB.")

    def __str__(self):
        return f"{self.student} - {self.assignment.title}"
