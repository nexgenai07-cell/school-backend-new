from rest_framework import serializers
from .models import (
    SkillMapping, AutomationRule, AutomationLog, AnalyticsSnapshot,
    Prediction, Recommendation, StudentGoal, StudentSkill, ParentEngagement,
)


class SkillMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillMapping
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class AutomationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationRule
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class AutomationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsSnapshot
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class StudentGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGoal
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class StudentSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSkill
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class ParentEngagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentEngagement
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']
