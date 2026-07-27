from rest_framework.routers import DefaultRouter
from .views import FeeStructureViewSet, ExpenseViewSet, FeeViewSet, PaymentViewSet, FeeHistoryViewSet

router = DefaultRouter()
router.register('fee-structures', FeeStructureViewSet, basename='fee-structures')
router.register('expenses', ExpenseViewSet, basename='expenses')
router.register('fees', FeeViewSet, basename='fees')
router.register('payments', PaymentViewSet, basename='payments')
router.register('fee-history', FeeHistoryViewSet, basename='fee-history')

urlpatterns = router.urls
