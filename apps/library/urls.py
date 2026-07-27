from rest_framework.routers import DefaultRouter
from .views import BookViewSet, BookIssueViewSet, BookIssueHistoryViewSet

router = DefaultRouter()
router.register('books', BookViewSet, basename='books')
router.register('book-issues', BookIssueViewSet, basename='book-issues')
router.register('book-issue-history', BookIssueHistoryViewSet, basename='book-issue-history')

urlpatterns = router.urls
