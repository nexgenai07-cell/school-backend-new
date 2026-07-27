from rest_framework import serializers
from .models import Department, Employee, Leave, Payroll, SalaryHistory, LeaveHistory


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = '__all__'
        read_only_fields = ['status']  # ✅ Default: status read-only

    # ✅ FIX #3: Only admin can set status to approved/rejected
    def validate_status(self, value):
        request = self.context.get('request')
        if request and request.user.role != 'admin':
            if value in ['approved', 'rejected']:
                raise serializers.ValidationError(
                    "Only admin can approve or reject leave requests."
                )
        return value

    def create(self, validated_data):
        # ✅ Always set status to 'pending' on creation
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class PayrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payroll
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted', 'net_salary']
class SalaryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class LeaveHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']
