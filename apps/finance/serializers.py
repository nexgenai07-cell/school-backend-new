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
        from .models import Payment
        total_paid = Payment.objects.filter(fee=fee).aggregate(total=serializers.models.Sum('amount_paid'))['total'] or 0
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
