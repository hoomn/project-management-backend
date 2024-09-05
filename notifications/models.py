from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings

from core.mixins import TimestampMixin
from core.utils import get_timesince

from .mixins import NotificationMixin


class Notification(TimestampMixin):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="%(class)s", on_delete=models.CASCADE)
    viewed = models.BooleanField(verbose_name="Has been viewed", default=False)
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.content_type} Notification fot {self.user}"

    def time_since_creation(self):
        return get_timesince(self.created_at)

    def get_related_verbose_name(self):
        if self.content_object:
            related_obj = self.content_object
            if hasattr(related_obj, "get_verbose_name"):
                return related_obj.get_verbose_name().title()
        return None

    def get_related_url(self):
        if self.content_object:
            related_obj = self.content_object
            if hasattr(related_obj, "get_absolute_url"):
                return related_obj.get_absolute_url()
        return None

    class Meta:
        indexes = [models.Index(fields=["content_type", "object_id"])]
        ordering = ["-created_at"]


class Category(models.Model):

    action = models.CharField(max_length=1, choices=NotificationMixin.Action_Choices)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"app_label": "pm", "model__in": ("project", "task", "subtask")},
    )

    class Meta:
        verbose_name = "Notification Category"
        verbose_name_plural = "Notification Categories"
        constraints = [models.UniqueConstraint(fields=["action", "content_type"], name="unique_action_content_type")]

    def __str__(self):
        return f"{self.content_type} ({self.action})"


class EmailLog(models.Model):

    class Status(models.IntegerChoices):
        FAIL = 0, "Failed"
        SUCCESS = 1, "Succeed"

    email = models.CharField(max_length=100)
    status = models.PositiveSmallIntegerField(choices=Status, default=Status.FAIL)
    description = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Truncate description if it exceeds 1024 characters
        if len(self.description) > 128:
            self.content = self.content[:128]

        super().save(*args, **kwargs)
