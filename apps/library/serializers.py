from rest_framework import serializers
from .models import Book, BookIssue, BookIssueHistory


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class BookIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookIssue
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']


class BookIssueHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookIssueHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']
