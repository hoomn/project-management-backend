from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils import timezone

from notifications.models import Notification


class UserManager(BaseUserManager):
    """
    Define a model manager for User model with no username field.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular User with the given email and password.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class SingleUseCodeManager(models.Manager):
    """
    Define a model manager for UseCodeManager model.
    """

    def create(self, **kwargs):

        # Calculate the expiration time (15 minutes from now)
        expiration_time = timezone.now() + timezone.timedelta(minutes=15)

        # If a code already exists for this user, update it
        single_use_code, created = self.model.objects.update_or_create(
            defaults={
                "code": self.generate_code(),
                "expires_at": expiration_time,
                "is_used": False,
                **kwargs,
            }
        )

        # Notify the user via email when a single-use code is created
        Notification.objects.create(
            user=single_use_code.user, content_object=single_use_code
        )

        return single_use_code

    def generate_code(self):
        import uuid

        return uuid.uuid4()
