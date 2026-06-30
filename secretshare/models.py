import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone


def default_expiry():
    return timezone.now() + timedelta(days=7)


class Secret(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField(help_text="The secret content to share.")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        default=default_expiry,
        help_text="Secret becomes invalid after this time even if never viewed.",
    )
    viewed_at = models.DateTimeField(null=True, blank=True, editable=False)

    def is_expired(self):
        if self.viewed_at is not None:
            return True
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False

    is_expired.boolean = True

    def __str__(self):
        return f"Secret {self.id} (created {self.created_at:%Y-%m-%d})"
