from rest_framework import viewsets
from apps.common.permissions import ReadOnlyOrAdmin, FinancePermission
from .models import FeeStructure, Expense, Fee, Payment, FeeHistory
from .serializers import (
    FeeStructureSerializer, ExpenseSerializer, FeeSerializer,
    PaymentSerializer, FeeHistorySerializer,
)


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [ReadOnlyOrAdmin]


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [FinancePermission]


class FeeViewSet(viewsets.ModelViewSet):
    serializer_class = FeeSerializer
    permission_classes = [FinancePermission]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Fee.objects.all()
        if user.role == 'student':
            return Fee.objects.filter(student__user=user)
        if user.role == 'parent':
            return Fee.objects.filter(student__parent__user=user)
        return Fee.objects.none()


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [FinancePermission]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Payment.objects.all()
        if user.role == 'student':
            return Payment.objects.filter(fee__student__user=user)
        if user.role == 'parent':
            return Payment.objects.filter(fee__student__parent__user=user)
        return Payment.objects.none()


class FeeHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = FeeHistorySerializer
    permission_classes = [FinancePermission]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return FeeHistory.objects.all()
        if user.role == 'student':
            return FeeHistory.objects.filter(fee__student__user=user)
        if user.role == 'parent':
            return FeeHistory.objects.filter(fee__student__parent__user=user)
        return FeeHistory.objects.none()