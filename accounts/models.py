from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from core.mixins import TimestampMixin
from notifications.mixins import NotificationMixin
from .managers import UserManager, SingleUseCodeManager

from uuid import uuid4


class User(AbstractUser, TimestampMixin):

    username = None
    email = models.EmailField(
        max_length=100,
        unique=True,
        blank=False,
        error_messages={"unique": "A user with that email already exists."},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def initial(self):
        if self.first_name and self.last_name:
            return self.first_name[0].upper() + self.last_name[0].upper()
        return "__"

    objects = UserManager()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notification = models.BooleanField(verbose_name="Receive Email Notification", default=True)


class SingleUseCode(NotificationMixin):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.UUIDField("Single-Use Code", default=uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False)

    objects = SingleUseCodeManager()

    class Meta(NotificationMixin.Meta):
        verbose_name = "single-use code"

    def __str__(self):
        return "*" * (12) + self.code.hex[-6:]

    def is_expired(self):
        return self.expires_at > timezone.now()

    def is_valid(self):
        return not self.is_used and not self.is_expired

    def get_absolute_url(self):
        return None

    def get_verbose_name(self):
        return self._meta.verbose_name

    def render_notification(self):
        if self.action == self.Action_Choices.CREATE:

            try:
                item = self.get_verbose_name()
            except:
                item = "single-use code"

            return {
                "subject": f"Notification: Your { item.title() }",
                "body": f"Your { item } is: { self.code }\n— PLEASE DO NOT SHARE THIS CODE.",
                "body_html": f"<p>Your { item } is below:</p><p>{ self.code }</p><p style='color:#cc0000'><strong>PLEASE DO NOT SHARE THIS CODE.</strong></p>",
            }
        else:
            raise NotImplementedError()


class AccessList(TimestampMixin):

    email = models.EmailField(max_length=100, unique=True, blank=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name_plural = "Access list"

    def __str__(self):
        return self.email
