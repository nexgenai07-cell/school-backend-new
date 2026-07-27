from rest_framework import viewsets
from apps.common.permissions import IsAssignedTeacherOrAdmin, IsOwnerParentOrAdmin
from apps.users.models import Student, Teacher, Parent
from .models import Assignment, Submission
from .serializers import AssignmentSerializer, SubmissionSerializer


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAssignedTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab assignments
        if user.role == 'admin':
            return Assignment.objects.all()
        
        # Teacher -> apne assignments
        if user.role == 'teacher':
            return Assignment.objects.filter(teacher__user=user)
        
        # Student -> apni class ki assignments
        if user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                if student.class_obj:
                    return Assignment.objects.filter(class_obj=student.class_obj)
                return Assignment.objects.none()
            except Student.DoesNotExist:
                return Assignment.objects.none()
        
        # Parent -> apne bachchon ki class ki assignments
        if user.role == 'parent':
            try:
                parent = Parent.objects.get(user=user)
                students = parent.children.all()
                class_ids = [s.class_obj_id for s in students if s.class_obj_id]
                if class_ids:
                    return Assignment.objects.filter(class_obj_id__in=class_ids).distinct()
                return Assignment.objects.none()
            except Parent.DoesNotExist:
                return Assignment.objects.none()
        
        return Assignment.objects.none()


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [IsOwnerParentOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab submissions
        if user.role == 'admin':
            return Submission.objects.all()
        
        # Teacher -> sirf apne assignments ki submissions
        if user.role == 'teacher':
            return Submission.objects.filter(assignment__teacher__user=user)
        
        # Student -> apni submissions
        if user.role == 'student':
            return Submission.objects.filter(student__user=user)
        
        # Parent -> apne bachchon ki submissions
        if user.role == 'parent':
            return Submission.objects.filter(student__parent__user=user)
        
        return Submission.objects.none()