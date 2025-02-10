from django.db import models
from django.contrib.auth.models import AbstractUser

from core.mixins import TimestampMixin

from .managers import UserManager


class User(AbstractUser, TimestampMixin):

    username = None
    email = models.EmailField(
        max_length=100,
        unique=True,
        blank=False,
        error_messages={"unique": "A user with that email already exists."},
    )
    email_notification = models.BooleanField(verbose_name="Receive Email Notification", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.full_name if self.full_name else self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def initials(self):
        if self.first_name and self.last_name:
            return self.first_name[0].upper() + self.last_name[0].upper()
        return "__"

    objects = UserManager()
