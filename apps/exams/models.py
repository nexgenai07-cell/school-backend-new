from apps.common.models import BaseModel
from django.db import models


class GradeScale(BaseModel):
    grade = models.CharField(max_length=10, unique=True)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    gpa = models.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        db_table = 'grade_scale'

    def __str__(self):
        return self.grade


class Exam(BaseModel):
    EXAM_TYPE_CHOICES = [('term', 'Term'), ('quiz', 'Quiz'), ('annual', 'Annual')]

    name = models.CharField(max_length=150)
    class_obj = models.ForeignKey('academics.Class', on_delete=models.CASCADE, related_name='exams')
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='exams')
    teacher = models.ForeignKey('users.Teacher', on_delete=models.SET_NULL, null=True, related_name='exams')
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    date = models.DateField()
    total_marks = models.IntegerField()
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'exams'
        # ✅ Yeh constraint database level pe duplicate rokega
        unique_together = ['class_obj', 'subject', 'exam_type']

    def __str__(self):
        return self.name

class Question(BaseModel):
    QUESTION_TYPE_CHOICES = [('mcq', 'MCQ'), ('short', 'Short'), ('long', 'Long')]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    answer_text = models.TextField(blank=True, help_text="Model answer")
    marks = models.IntegerField()
    options = models.JSONField(null=True, blank=True, help_text="MCQ options")
    correct_answer = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'questions'

    def __str__(self):
        return f"Q{self.id} - {self.exam.name}"


class StudentAnswer(BaseModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='student_answers')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='exam_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    answer_text = models.TextField(blank=True)
    selected_option = models.CharField(max_length=255, blank=True, help_text="For MCQ")
    is_correct = models.BooleanField(null=True, blank=True, help_text="AI checked")
    marks_awarded = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'student_answers'

    def __str__(self):
        return f"{self.student} - Q{self.question_id}"


class Result(BaseModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True)
    grade = models.ForeignKey(GradeScale, on_delete=models.SET_NULL, null=True, blank=True, to_field='grade', related_name='results')
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'results'

    def save(self, *args, **kwargs):
        if self.exam.total_marks:
            self.percentage = round((self.marks_obtained / self.exam.total_marks) * 100, 2)
        matched_grade = GradeScale.objects.filter(
            min_percentage__lte=self.percentage,
            max_percentage__gte=self.percentage,
        ).first()
        if matched_grade:
            self.grade = matched_grade
            self.gpa = matched_grade.gpa
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.exam.name}"

class AIAutoChecking(BaseModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='ai_checks')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='ai_checks')
    ai_score = models.DecimalField(max_digits=5, decimal_places=2)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)
    checked_at = models.DateTimeField(auto_now_add=True)
    checked_by_ai = models.BooleanField(default=True)
    reviewed_by_teacher = models.ForeignKey('users.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_reviews')

    class Meta:
        db_table = 'ai_auto_checking'

    def __str__(self):
        return f"{self.student} - {self.exam.name} (AI)"
