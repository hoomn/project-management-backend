from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient

from accounts.models import User, SingleUseCode, AccessList


class SingleUseCodeTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user-request-single-use-code")
        AccessList.objects.create(email="test@example.com")
        AccessList.objects.create(email="test1@example.com")
        AccessList.objects.create(email="test2@example.com")

    def test_successful_request(self):
        response = self.client.post(self.url, {"email": "test@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)

    def test_rate_limiting(self):
        # First request should succeed
        response1 = self.client.post(self.url, {"email": "test@example.com"})
        self.assertEqual(response1.status_code, 200)

        # Second request within a minute should fail
        response2 = self.client.post(self.url, {"email": "test@example.com"})
        self.assertEqual(response2.status_code, 429)
        self.assertIn("error", response2.data)

    def test_different_emails(self):
        # Requests for different emails should both succeed
        response1 = self.client.post(self.url, {"email": "test1@example.com"})
        self.assertEqual(response1.status_code, 200)

        response2 = self.client.post(self.url, {"email": "test2@example.com"})
        self.assertEqual(response2.status_code, 200)

    def test_rate_limit_reset(self):
        # First request
        self.client.post(self.url, {"email": "test@example.com"})

        # Simulate time passing
        user = User.objects.filter(email="test@example.com").first()
        SingleUseCode.objects.filter(user=user).update(
            expires_at=timezone.now() - timezone.timedelta(minutes=15)
        )

        # Request after rate limit period should succeed
        response = self.client.post(self.url, {"email": "test@example.com"})
        self.assertEqual(response.status_code, 200)

    def test_missing_email(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
