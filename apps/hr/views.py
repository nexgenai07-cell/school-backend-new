from rest_framework import viewsets
from apps.common.permissions import ReadOnlyOrAdmin, HRPermission, LeavePermission
from apps.users.models import Staff
from .models import Department, Employee, Leave, Payroll, SalaryHistory, LeaveHistory
from .serializers import (
    DepartmentSerializer, EmployeeSerializer, LeaveSerializer,
    PayrollSerializer, SalaryHistorySerializer, LeaveHistorySerializer,
)


def is_hr_staff(user):
    """Helper: checks if a staff user belongs to the HR department."""
    if user.role != 'staff':
        return False
    try:
        staff = Staff.objects.get(user=user)
        return bool(staff.department and staff.department.lower() == 'hr')
    except Staff.DoesNotExist:
        return False


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [ReadOnlyOrAdmin]


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [HRPermission]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            return Employee.objects.all()

        if user.role == 'staff':
            if is_hr_staff(user):
                return Employee.objects.all()
            return Employee.objects.filter(user=user)

        if user.role == 'teacher':
            return Employee.objects.filter(user=user)

        return Employee.objects.none()


class LeaveViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveSerializer
    permission_classes = [LeavePermission]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            return Leave.objects.all()

        if is_hr_staff(user):
            return Leave.objects.all()

        return Leave.objects.filter(employee__user=user)


class PayrollViewSet(viewsets.ModelViewSet):
    serializer_class = PayrollSerializer
    permission_classes = [HRPermission]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            return Payroll.objects.all()

        if is_hr_staff(user):
            return Payroll.objects.all()

        return Payroll.objects.filter(employee__user=user)


class SalaryHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = SalaryHistorySerializer
    permission_classes = [HRPermission]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            return SalaryHistory.objects.all()

        if is_hr_staff(user):
            return SalaryHistory.objects.all()

        return SalaryHistory.objects.filter(employee__user=user)


class LeaveHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveHistorySerializer
    permission_classes = [HRPermission]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            return LeaveHistory.objects.all()

        if is_hr_staff(user):
            return LeaveHistory.objects.all()

        return LeaveHistory.objects.filter(leave__employee__user=user)