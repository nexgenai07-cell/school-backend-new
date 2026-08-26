from django.test import TestCase

from apps.tenants.context import current_tenant
from apps.tenants.models import School
from apps.users.models import User


class TenantIsolationTests(TestCase):
    def create_user_for(self, school, email):
        token = current_tenant.set(school)
        try:
            return User.objects.create_user(
                email=email, name=email, password="safe-password", role="admin"
            )
        finally:
            current_tenant.reset(token)

    def test_default_manager_is_scoped_to_current_tenant(self):
        first = School.objects.create(name="First School", slug="first")
        second = School.objects.create(name="Second School", slug="second")
        first_user = self.create_user_for(first, "first@example.com")
        self.create_user_for(second, "second@example.com")

        token = current_tenant.set(first)
        try:
            self.assertEqual(list(User.objects.values_list("id", flat=True)), [first_user.id])
        finally:
            current_tenant.reset(token)

    def test_api_requests_require_a_tenant(self):
        response = self.client.get("/api/users/users/")
        self.assertEqual(response.status_code, 400)
