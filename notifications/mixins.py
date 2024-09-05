from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.db import models

from core.utils import get_timesince


class NotificationMixin(models.Model):

    class Action_Choices(models.TextChoices):
        CREATE = "C", "Create"
        UPDATE = "U", "Update"
        DELETE = "D", "Delete"

    action = models.CharField(max_length=1, choices=Action_Choices, default=Action_Choices.CREATE)
    content = models.JSONField(verbose_name="Content", default=dict)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name="%(class)s_created_by", on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def time_since_creation(self):
        return get_timesince(self.created_at)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def get_verbose_name(self):
        raise NotImplementedError("Subclasses must implement get_verbose_name()")

    def render_notification(self):
        raise NotImplementedError("Subclasses must implement render_notification()")

    def save(self, *args, **kwargs):

        if not hasattr(self, "action"):
            raise ImproperlyConfigured("NotificationMixin requires an 'action' field")

        super().save(*args, **kwargs)
