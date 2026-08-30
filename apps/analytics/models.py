from apps.common.models import BaseModel
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class SkillMapping(BaseModel):
    name = models.CharField(max_length=150, help_text="Skill name")
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'skill_mapping'
        # Per-school unique skill names.
        unique_together = ['school', 'name']

    def __str__(self):
        return self.name


class AutomationRule(BaseModel):
    rule_name = models.CharField(max_length=150)
    condition = models.TextField(help_text="JSON rule condition")
    action = models.TextField(help_text="What to trigger")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'automation_rules'
        # Same school cannot define two rules with the same name.
        unique_together = ['school', 'rule_name']

    def __str__(self):
        return self.rule_name


class AutomationLog(BaseModel):
    rule = models.ForeignKey(AutomationRule, on_delete=models.CASCADE, related_name='logs')
    triggered_at = models.DateTimeField(auto_now_add=True)
    result = models.TextField(blank=True)

    class Meta:
        db_table = 'automation_logs'
        # A rule cannot log two executions at the exact same timestamp.
        unique_together = ['rule', 'triggered_at']

    def __str__(self):
        return f"{self.rule.rule_name} - {self.triggered_at}"


class AnalyticsSnapshot(BaseModel):
    metric_name = models.CharField(max_length=150)
    metric_value = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField(help_text="Snapshot date")

    class Meta:
        db_table = 'analytics_snapshots'
        # One snapshot per metric per school per day.
        unique_together = ['school', 'metric_name', 'date']

    def __str__(self):
        return f"{self.metric_name} - {self.date}"


class Prediction(BaseModel):
    PREDICTION_TYPE_CHOICES = [('risk', 'Risk'), ('grade', 'Grade'), ('performance', 'Performance')]

    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='predictions')
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPE_CHOICES)
    value = models.CharField(max_length=150, help_text="Predicted outcome")
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    prediction_date = models.DateField()
    details = models.TextField(blank=True)

    class Meta:
        db_table = 'predictions'
        # One prediction per type per student per day.
        unique_together = ['student', 'prediction_type', 'prediction_date']

    def __str__(self):
        return f"{self.student} - {self.prediction_type}"


class Recommendation(BaseModel):
    TYPE_CHOICES = [('study_plan', 'Study Plan'), ('topic', 'Topic'), ('activity', 'Activity')]
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('ignored', 'Ignored')]

    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='recommendations')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'recommendations'
        # The exact same recommendation (same content) cannot be duplicated for a student.
        unique_together = ['student', 'type', 'content']

    def __str__(self):
        return f"{self.student} - {self.type}"


class StudentGoal(BaseModel):
    GOAL_TYPE_CHOICES = [('academic', 'Academic'), ('personal', 'Personal'), ('activity', 'Activity')]
    STATUS_CHOICES = [('active', 'Active'), ('completed', 'Completed')]

    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='goals')
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES)
    target = models.TextField()
    target_date = models.DateField(null=True, blank=True)
    progress = models.IntegerField(default=0, help_text="0-100%", validators=[MinValueValidator(0), MaxValueValidator(100)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        db_table = 'student_goals'
        # The exact same goal (same target text) cannot be duplicated for a student.
        unique_together = ['student', 'goal_type', 'target']

    def __str__(self):
        return f"{self.student} - {self.goal_type}"


class StudentSkill(BaseModel):
    PROFICIENCY_CHOICES = [('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')]

    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(SkillMapping, on_delete=models.CASCADE, related_name='student_skills')
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES)
    acquired_on = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'student_skills'
        # A student cannot have the same skill twice.
        unique_together = ['student', 'skill']

    def __str__(self):
        return f"{self.student} - {self.skill.name}"


class ParentEngagement(BaseModel):
    parent = models.ForeignKey('users.Parent', on_delete=models.CASCADE, related_name='engagement_records')
    engagement_score = models.IntegerField(default=0, help_text="0-100", validators=[MinValueValidator(0), MaxValueValidator(100)])
    ptm_attendance = models.IntegerField(default=0, help_text="Count", validators=[MinValueValidator(0)])
    response_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    interaction_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'parent_engagement'

    def __str__(self):
        return f"{self.parent} - {self.engagement_score}"
