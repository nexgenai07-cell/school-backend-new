from rest_framework import viewsets
from apps.common.permissions import LibraryPermission
from apps.users.models import Student, Teacher, Parent
from .models import Book, BookIssue, BookIssueHistory
from .serializers import BookSerializer, BookIssueSerializer, BookIssueHistorySerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [LibraryPermission]

    # Optional: Filter available books for students/parents
    def get_queryset(self):
        user = self.request.user
        
        # Admin, Staff, Teacher -> sab books
        if user.role in ['admin', 'staff', 'teacher']:
            return Book.objects.all()
        
        # Student, Parent -> sab books (lekin available filter optional)
        if user.role in ['student', 'parent']:
            # Sirf available books dikhana chahte hain toh:
            # return Book.objects.filter(available_copies__gt=0)
            return Book.objects.all()
        
        return Book.objects.none()


class BookIssueViewSet(viewsets.ModelViewSet):
    serializer_class = BookIssueSerializer
    permission_classes = [LibraryPermission]

    def get_queryset(self):
        user = self.request.user
        
        # Admin, Staff -> sab book issues
        if user.role in ['admin', 'staff']:
            return BookIssue.objects.all()
        
        # Teacher -> apne students ki book issues
        if user.role == 'teacher':
            return BookIssue.objects.filter(
                student__class_obj__class_subjects__teacher__user=user
            ).distinct()
        
        # Student -> apni book issues
        if user.role == 'student':
            return BookIssue.objects.filter(student__user=user)
        
        # Parent -> bachchon ki book issues
        if user.role == 'parent':
            return BookIssue.objects.filter(student__parent__user=user)
        
        return BookIssue.objects.none()


class BookIssueHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = BookIssueHistorySerializer
    permission_classes = [LibraryPermission]

    def get_queryset(self):
        user = self.request.user
        
        # Admin, Staff -> sab history
        if user.role in ['admin', 'staff']:
            return BookIssueHistory.objects.all()
        
        # Teacher -> apne students ki history
        if user.role == 'teacher':
            return BookIssueHistory.objects.filter(
                book_issue__student__class_obj__class_subjects__teacher__user=user
            ).distinct()
        
        # Student -> apni history
        if user.role == 'student':
            return BookIssueHistory.objects.filter(book_issue__student__user=user)
        
        # Parent -> bachchon ki history
        if user.role == 'parent':
            return BookIssueHistory.objects.filter(book_issue__student__parent__user=user)
        
        return BookIssueHistory.objects.none()