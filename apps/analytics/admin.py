from django.contrib import admin
from .models import (
    SkillMapping, AutomationRule, AutomationLog, AnalyticsSnapshot,
    Prediction, Recommendation, StudentGoal, StudentSkill, ParentEngagement,
)

admin.site.register(SkillMapping)
admin.site.register(AutomationRule)
admin.site.register(AutomationLog)
admin.site.register(AnalyticsSnapshot)
admin.site.register(Prediction)
admin.site.register(Recommendation)
admin.site.register(StudentGoal)
admin.site.register(StudentSkill)
admin.site.register(ParentEngagement)
