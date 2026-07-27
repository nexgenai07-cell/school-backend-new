from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.permissions import IsOwnerParentOrAdmin
from apps.users.models import Student, Teacher, Parent
from .models import Attendance, BehaviorLog
from .serializers import AttendanceSerializer, BehaviorLogSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsOwnerParentOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab
        if user.role == 'admin':
            return Attendance.objects.all()
        
        # Teacher -> sirf apne students ki attendance
        if user.role == 'teacher':
            return Attendance.objects.filter(
                student__class_obj__class_subjects__teacher__user=user
            ).distinct()
        
        # Student -> apni attendance
        if user.role == 'student':
            return Attendance.objects.filter(student__user=user)
        
        # Parent -> bachchon ki attendance
        if user.role == 'parent':
            return Attendance.objects.filter(student__parent__user=user)
        
        return Attendance.objects.none()

    @action(detail=False, methods=['get'], url_path='monthly-summary')
    def monthly_summary(self, request):
        user = request.user
        student_id = request.query_params.get('student_id')
        month = request.query_params.get('month')
        
        if not student_id or not month:
            return Response({"error": "student_id and month are required"}, status=400)
        
        # ✅ Security Check - Student ka data dekhne ka permission hai?
        try:
            student = Student.objects.get(id=student_id)
            
            # Admin -> sab allow
            if user.role == 'admin':
                pass
            # Teacher -> apna student
            elif user.role == 'teacher':
                if not Attendance.objects.filter(
                    student_id=student_id,
                    student__class_obj__class_subjects__teacher__user=user
                ).exists():
                    return Response({"error": "You don't have permission to view this student's attendance"}, status=403)
            # Student -> sirf apna
            elif user.role == 'student':
                if student.user_id != user.id:
                    return Response({"error": "You can only view your own attendance"}, status=403)
            # Parent -> apna bachcha
            elif user.role == 'parent':
                if student.parent.user_id != user.id:
                    return Response({"error": "You can only view your children's attendance"}, status=403)
            else:
                return Response({"error": "You don't have permission"}, status=403)
                
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

        records = Attendance.objects.filter(student_id=student_id, date__startswith=month)
        total = records.count()
        present = records.filter(status='present').count()
        percentage = round((present / total) * 100, 2) if total else 0

        return Response({
            "student_id": student_id,
            "student_name": student.user.name,
            "month": month,
            "total_days": total,
            "present_days": present,
            "absent_days": total - present,
            "attendance_percentage": percentage,
        })


class BehaviorLogViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorLogSerializer
    permission_classes = [IsOwnerParentOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Admin -> sab
        if user.role == 'admin':
            return BehaviorLog.objects.all()
        
        # Teacher -> sirf apne students ke behavior logs
        if user.role == 'teacher':
            return BehaviorLog.objects.filter(
                student__class_obj__class_subjects__teacher__user=user
            ).distinct()
        
        # Student -> apne behavior logs
        if user.role == 'student':
            return BehaviorLog.objects.filter(student__user=user)
        
        # Parent -> bachchon ke behavior logs
        if user.role == 'parent':
            return BehaviorLog.objects.filter(student__parent__user=user)
        
        return BehaviorLog.objects.none()