from rest_framework import serializers
from .models import FeeStructure, Expense, Fee, Payment, FeeHistory


class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class PaymentSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = FeeHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']
