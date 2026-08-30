from rest_framework import serializers
from .models import FeeStructure, Expense, Fee, Payment, FeeHistory


class FeeStructureSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_obj.name', read_only=True)

    class Meta:
        model = FeeStructure
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class ExpenseSerializer(serializers.ModelSerializer):
    paid_by_name = serializers.CharField(source='paid_by.name', read_only=True, default=None)

    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate_paid_by(self, value):
        # Business rule: expenses are recorded by admins only.
        if value and value.role != 'admin':
            raise serializers.ValidationError(
                "Only admin users can be recorded as paid_by for an expense."
            )
        return value


class FeeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.name', read_only=True)
    fee_structure_title = serializers.CharField(source='fee_structure.title', read_only=True)

    class Meta:
        model = Fee
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='fee.student.user.name', read_only=True)
    fee_title = serializers.CharField(source='fee.fee_structure.title', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate(self, data):
        fee = data.get('fee') or getattr(self.instance, 'fee', None)
        amount_paid = data.get('amount_paid')
        payment_date = data.get('payment_date') or getattr(self.instance, 'payment_date', None)

        if payment_date:
            from django.utils import timezone
            if payment_date > timezone.localdate():
                raise serializers.ValidationError(
                    "Payment date cannot be in the future."
                )

        if amount_paid is not None and amount_paid <= 0:
            raise serializers.ValidationError("Amount paid must be greater than zero.")

        if fee and amount_paid is not None:
            from django.db.models import Sum
            from .models import Payment
            total_paid = Payment.objects.filter(fee=fee).aggregate(
                total=Sum('amount_paid')
            )['total'] or 0
            if self.instance:
                total_paid -= self.instance.amount_paid
            if total_paid + amount_paid > fee.amount:
                raise serializers.ValidationError(
                    f"Payment exceeds remaining fee balance ({fee.amount - total_paid} left)."
                )
        return data

class FeeHistorySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='fee.student.user.name', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.name', read_only=True, default=None)

    class Meta:
        model = FeeHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate_changed_by(self, value):
        # Business rule: fee status/amount changes may only be attributed to admins.
        if value and value.role != 'admin':
            raise serializers.ValidationError(
                "Only admin users can be recorded as changed_by."
            )
        return value
