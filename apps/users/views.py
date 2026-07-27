from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.permissions import (
    IsAdmin, IsAdminOrTeacherOrParent, IsAdminOrTeacherOrStudentOrParent, IsSelfOrAdmin,
)
from .models import User, Student, Teacher, Staff, Parent
from .serializers import (
    UserSerializer, StudentSerializer, TeacherSerializer, 
    StaffSerializer, ParentSerializer, RegisterSerializer
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrTeacherOrParent]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Student.objects.all()
        if user.role == 'teacher':
            return Student.objects.filter(
                class_obj__class_subjects__teacher__user=user
            ).distinct()
        if user.role == 'parent':
            return Student.objects.filter(parent__user=user)
        if user.role == 'student':
            return Student.objects.filter(user=user)
        return Student.objects.none()

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current student profile"""
        user = request.user
        
        # ✅ Check if user is authenticated
        if not user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=401
            )
        
        # ✅ Only students can access
        if user.role != 'student':
            return Response(
                {"error": "Only students can access this endpoint"},
                status=403
            )
        
        try:
            student = Student.objects.get(user=user)
            serializer = self.get_serializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {"error": "Student profile not found"},
                status=404
            )


class TeacherViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherSerializer
    permission_classes = [IsAdminOrTeacherOrStudentOrParent]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Teacher.objects.all()
        if user.role == 'teacher':
            return Teacher.objects.filter(user=user)
        if user.role == 'student':
            return Teacher.objects.filter(
                class_subjects__class_obj__students__user=user
            ).distinct()
        if user.role == 'parent':
            return Teacher.objects.filter(
                class_subjects__class_obj__students__parent__user=user
            ).distinct()
        return Teacher.objects.none()

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current teacher profile"""
        user = request.user
        
        if not user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)
        
        if user.role != 'teacher':
            return Response({"error": "Only teachers can access this endpoint"}, status=403)
        
        try:
            teacher = Teacher.objects.get(user=user)
            serializer = self.get_serializer(teacher)
            return Response(serializer.data)
        except Teacher.DoesNotExist:
            return Response({"error": "Teacher profile not found"}, status=404)


class StaffViewSet(viewsets.ModelViewSet):
    serializer_class = StaffSerializer
    permission_classes = [IsAdminOrTeacherOrParent]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'teacher', 'parent']:
            return Staff.objects.all()
        return Staff.objects.none()

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current staff profile"""
        user = request.user
        
        if not user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)
        
        if user.role != 'staff':
            return Response({"error": "Only staff can access this endpoint"}, status=403)
        
        try:
            staff = Staff.objects.get(user=user)
            serializer = self.get_serializer(staff)
            return Response(serializer.data)
        except Staff.DoesNotExist:
            return Response({"error": "Staff profile not found"}, status=404)


class ParentViewSet(viewsets.ModelViewSet):
    serializer_class = ParentSerializer
    permission_classes = [IsAdminOrTeacherOrParent]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'teacher']:
            return Parent.objects.all()
        if user.role == 'parent':
            return Parent.objects.filter(user=user)
        return Parent.objects.none()

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current parent profile"""
        user = request.user
        
        if not user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)
        
        if user.role != 'parent':
            return Response({"error": "Only parents can access this endpoint"}, status=403)
        
        try:
            parent = Parent.objects.get(user=user)
            serializer = self.get_serializer(parent)
            return Response(serializer.data)
        except Parent.DoesNotExist:
            return Response({"error": "Parent profile not found"}, status=404)