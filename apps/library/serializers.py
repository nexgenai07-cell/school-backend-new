from rest_framework import serializers
from .models import Book, BookIssue, BookIssueHistory


class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)

    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class BookIssueSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    student_name = serializers.CharField(source='student.user.name', read_only=True)

    class Meta:
        model = BookIssue
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate(self, data):
        book = data.get('book') or getattr(self.instance, 'book', None)
        student = data.get('student') or getattr(self.instance, 'student', None)

        # Validation 1: Same book already issued
        if student and book:
            existing_issue = BookIssue.objects.filter(
                student=student,
                book=book,
                status__in=['issued', 'overdue']
            ).exclude(id=getattr(self.instance, 'id', None))
            if existing_issue.exists():
                raise serializers.ValidationError(
                    f"{student.user.name} has already issued '{book.title}' and not returned it yet."
                )

        # Validation 2: Overdue books check
        if student:
            overdue_books = BookIssue.objects.filter(
                student=student,
                status='overdue'
            ).exclude(id=getattr(self.instance, 'id', None))
            if overdue_books.exists():
                book_titles = [issue.book.title for issue in overdue_books]
                raise serializers.ValidationError(
                    f"{student.user.name} has overdue book(s): {', '.join(book_titles)}. "
                    f"Please return them before issuing a new book."
                )

        # Validation 3: Max books limit
        if student:
            max_allowed = 3
            current_issued = BookIssue.objects.filter(
                student=student,
                status__in=['issued', 'overdue']
            ).exclude(id=getattr(self.instance, 'id', None)).count()
            if current_issued >= max_allowed:
                raise serializers.ValidationError(
                    f"{student.user.name} has already issued {current_issued} book(s). "
                    f"Maximum {max_allowed} books allowed at a time."
                )

        # Validation 4: Available copies
        if book and book.available_copies <= 0:
            raise serializers.ValidationError(
                f"No copies of '{book.title}' are available right now."
            )

        return data


class BookIssueHistorySerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book_issue.book.title', read_only=True)
    student_name = serializers.CharField(source='book_issue.student.user.name', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.name', read_only=True, default=None)

    class Meta:
        model = BookIssueHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']