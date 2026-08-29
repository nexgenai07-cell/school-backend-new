from rest_framework import serializers
from .models import Department, Employee, Leave, Payroll, SalaryHistory, LeaveHistory


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class EmployeeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)

    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.name', read_only=True)

    class Meta:
        model = Leave
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']
        # NOTE: 'status' yahan se hataya — warna admin bhi approve/reject nahi kar payega,
        # DRF read-only field ko input se pehle hi drop kar deta hai, validator chalta hi nahi

    def validate(self, data):
        request = self.context.get('request')
        employee = data.get('employee') or getattr(self.instance, 'employee', None)
        start_date = data.get('start_date') or getattr(self.instance, 'start_date', None)
        end_date = data.get('end_date') or getattr(self.instance, 'end_date', None)

        # NEW: non-admin sirf apni khud ki leave create/edit kar sake
        if request and request.user.role != 'admin' and employee is not None:
            if employee.user_id != request.user.id:
                raise serializers.ValidationError(
                    "You can only submit or edit leave requests for yourself."
                )

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("start_date cannot be after end_date.")

        if employee and start_date and end_date:
            overlapping = Leave.objects.filter(
                employee=employee,
                start_date__lte=end_date,
                end_date__gte=start_date,
            ).exclude(status='rejected')
            if self.instance:
                overlapping = overlapping.exclude(id=self.instance.id)
            if overlapping.exists():
                raise serializers.ValidationError(
                    f"{employee} already has a leave request overlapping these dates."
                )

        return data

    def validate_status(self, value):
        request = self.context.get('request')
        if request and value in ['approved', 'rejected'] and request.user.role != 'admin':
            raise serializers.ValidationError("Only admin can approve or reject leave requests.")
        return value

    def create(self, validated_data):
        # Naya leave request hamesha 'pending' se shuru ho, chahe kuch bhi bheja ho
        validated_data['status'] = 'pending'
        return super().create(validated_data)

class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.name', read_only=True)

    class Meta:
        model = Payroll
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted', 'net_salary']
class SalaryHistorySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.name', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.name', read_only=True, default=None)

    class Meta:
        model = SalaryHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class LeaveHistorySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='leave.employee.user.name', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.name', read_only=True, default=None)

    class Meta:
        model = LeaveHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']
