from rest_framework import viewsets
from apps.common.permissions import ReadOnlyOrAdmin, AutomationPermission, IsOwnerParentOrAdmin
from apps.users.models import Student, Teacher, Parent
from .models import (
    SkillMapping, AutomationRule, AutomationLog, AnalyticsSnapshot,
    Prediction, Recommendation, StudentGoal, StudentSkill, ParentEngagement,
)
from .serializers import (
    SkillMappingSerializer, AutomationRuleSerializer, AutomationLogSerializer,
    AnalyticsSnapshotSerializer, PredictionSerializer, RecommendationSerializer,
    StudentGoalSerializer, StudentSkillSerializer, ParentEngagementSerializer,
)


class SkillMappingViewSet(viewsets.ModelViewSet):
    queryset = SkillMapping.objects.all()
    serializer_class = SkillMappingSerializer
    permission_classes = [ReadOnlyOrAdmin]


class AutomationRuleViewSet(viewsets.ModelViewSet):
    queryset = AutomationRule.objects.all()
    serializer_class = AutomationRuleSerializer
    permission_classes = [AutomationPermission]


class AutomationLogViewSet(viewsets.ModelViewSet):
    queryset = AutomationLog.objects.all()
    serializer_class = AutomationLogSerializer
    permission_classes = [AutomationPermission]


class AnalyticsSnapshotViewSet(viewsets.ModelViewSet):
    queryset = AnalyticsSnapshot.objects.all()
    serializer_class = AnalyticsSnapshotSerializer
    permission_classes = [AutomationPermission]


class PredictionViewSet(viewsets.ModelViewSet):
    serializer_class = PredictionSerializer
    permission_classes = [IsOwnerParentOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab
        if user.role == 'admin':
            return Prediction.objects.all()
        
        # Teacher -> sirf apne students ki predictions
        if user.role == 'teacher':
            return Prediction.objects.filter(
                student__class_obj__class_subjects__teacher__user=user
            ).distinct()
        
        # Student -> apni predictions
        if user.role == 'student':
            return Prediction.objects.filter(student__user=user)
        
        # Parent -> bachchon ki predictions
        if user.role == 'parent':
            return Prediction.objects.filter(student__parent__user=user)
        
        return Prediction.objects.none()


class RecommendationViewSet(viewsets.ModelViewSet):
    serializer_class = RecommendationSerializer
    permission_classes = [IsOwnerParentOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab
        if user.role == 'admin':
            return Recommendation.objects.all()
        
        # Teacher -> sirf apne students ki recommendations
        if user.role == 'teacher':
            return Recommendation.objects.filter(
                student__class_obj__class_subjects__teacher__user=user
            ).distinct()
        
        # Student -> apni recommendations
        if user.role == 'student':
            return Recommendation.objects.filter(student__user=user)
        
        # Parent -> bachchon ki recommendations
        if user.role == 'parent':
            return Recommendation.objects.filter(student__parent__user=user)
        
        return Recommendation.objects.none()


class StudentGoalViewSet(viewsets.ModelViewSet):
    serializer_class = StudentGoalSerializer
    permission_classes = [IsOwnerParentOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab
        if user.role == 'admin':
            return StudentGoal.objects.all()
        
        # Teacher -> sirf apne students ke goals
        if user.role == 'teacher':
            return StudentGoal.objects.filter(
                student__class_obj__class_subjects__teacher__user=user
            ).distinct()
        
        # Student -> apne goals
        if user.role == 'student':
            return StudentGoal.objects.filter(student__user=user)
        
        # Parent -> bachchon ke goals
        if user.role == 'parent':
            return StudentGoal.objects.filter(student__parent__user=user)
        
        return StudentGoal.objects.none()


class StudentSkillViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSkillSerializer
    permission_classes = [IsOwnerParentOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab
        if user.role == 'admin':
            return StudentSkill.objects.all()
        
        # Teacher -> sirf apne students ki skills
        if user.role == 'teacher':
            return StudentSkill.objects.filter(
                student__class_obj__class_subjects__teacher__user=user
            ).distinct()
        
        # Student -> apni skills
        if user.role == 'student':
            return StudentSkill.objects.filter(student__user=user)
        
        # Parent -> bachchon ki skills
        if user.role == 'parent':
            return StudentSkill.objects.filter(student__parent__user=user)
        
        return StudentSkill.objects.none()


class ParentEngagementViewSet(viewsets.ModelViewSet):
    serializer_class = ParentEngagementSerializer
    permission_classes = [IsOwnerParentOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab
        if user.role == 'admin':
            return ParentEngagement.objects.all()
        
        # Teacher -> apne students ke parents ki engagement
        if user.role == 'teacher':
            return ParentEngagement.objects.filter(
                parent__children__class_obj__class_subjects__teacher__user=user
            ).distinct()
        
        # Parent -> apni engagement
        if user.role == 'parent':
            return ParentEngagement.objects.filter(parent__user=user)
        
        return ParentEngagement.objects.none()