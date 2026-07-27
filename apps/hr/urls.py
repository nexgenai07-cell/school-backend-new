from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, EmployeeViewSet, LeaveViewSet,
    PayrollViewSet, SalaryHistoryViewSet, LeaveHistoryViewSet,
)

router = DefaultRouter()
router.register('departments', DepartmentViewSet, basename='departments')
router.register('employees', EmployeeViewSet, basename='employees')
router.register('leaves', LeaveViewSet, basename='leaves')
router.register('payroll', PayrollViewSet, basename='payroll')
router.register('salary-history', SalaryHistoryViewSet, basename='salary-history')
router.register('leave-history', LeaveHistoryViewSet, basename='leave-history')

urlpatterns = router.urls
