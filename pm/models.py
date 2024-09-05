from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from core.mixins import TimestampMixin

from notifications.mixins import NotificationMixin

from .mixins import BaseItemMixin, BaseGenericMixin
from .utils import attachment_upload_path

from uuid import uuid4
import os


USER = settings.AUTH_USER_MODEL


class Attachment(BaseGenericMixin):

    file = models.FileField(upload_to=attachment_upload_path)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.file_name

    @property
    def extension(self):
        _, ext = os.path.splitext(self.file.name)
        return ext[1:]

    def save(self, *args, **kwargs):
        # Update original file_name and file_size before saving
        if not self.pk:
            self.file_name = self.file.name
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the model before the file
        super().delete(*args, **kwargs)
        # Delete the file from the storage backend
        if self.file:
            self.file.delete(save=False)


class Comment(BaseGenericMixin):

    text = models.TextField()

    def __str__(self):
        return self.text


class Activity(NotificationMixin):

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta(NotificationMixin.Meta):
        verbose_name = "activity"
        verbose_name_plural = "activities"
        indexes = [models.Index(fields=["content_type", "object_id"])]

    def __str__(self):
        return f"{self.get_action_display()} {self.content_type} object: {self.object_id} at {self.created_at}"

    def get_verbose_name(self):
        if self.content_object:
            related_obj = self.content_object
            if hasattr(related_obj, "get_verbose_name"):
                return related_obj.get_verbose_name()
        return self._meta.verbose_name

    def get_absolute_url(self):
        if self.content_object:
            related_obj = self.content_object
            if hasattr(related_obj, "get_absolute_url"):
                return related_obj.get_absolute_url()
        return None

    def render_notification(self):

        try:
            item = self.get_verbose_name()
        except:
            item = "item"

        if self.action == self.Action_Choices.CREATE:
            return {
                "subject": f"Notification: New {item.title()}",
                "body": f"A new {item} has been added.",
                "body_html": f"<p>A new {item} has been added.</p>",
            }

        elif self.action == self.Action_Choices.UPDATE:
            return {
                "subject": f"Notification: {item.title()} Updated",
                "body": f"Your {item} has been updated.",
                "body_html": f"<p>Your {item} has been updated.</p>",
            }

        elif self.action == self.Action_Choices.DELETE:
            return {
                "subject": f"Notification: {item.title()} Deleted",
                "body": f"Your {item} has been deleted.",
                "body_html": f"<p>Your {item} has been deleted.</p>",
            }


class Domain(TimestampMixin):

    uuid = models.UUIDField(unique=True, editable=False, default=uuid4)
    title = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(USER, blank=True, related_name="%(class)s_membership")
    created_by = models.ForeignKey(
        USER, blank=True, null=True, related_name="%(class)s_created_by", on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.title


class Project(BaseItemMixin):
    """
    This model allows for quick entry of a project by requiring only the essential fields.
    """

    domain = models.ForeignKey(
        Domain,
        verbose_name="Parent Domain",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )

    class Meta(BaseItemMixin.Meta):
        constraints = [models.UniqueConstraint(fields=["domain", "title"], name="unique_domain_title")]

    def archive(self):
        super().archive()
        self.tasks.update(is_archived=True)
        Subtask.objects.filter(task__project=self).update(is_archived=True)


class Task(BaseItemMixin):
    """
    This model allows for quick entry of a task by requiring only the essential fields.
    """

    project = models.ForeignKey(
        Project,
        verbose_name="Parent Project",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )

    class Meta(BaseItemMixin.Meta):
        constraints = [models.UniqueConstraint(fields=["project", "title"], name="unique_project_title")]

    def archive(self):
        super().archive()
        self.subtasks.update(is_archived=True)


class Subtask(BaseItemMixin):
    """
    This model allows for quick entry of a subtask by requiring only the essential fields.
    """

    task = models.ForeignKey(
        Task,
        verbose_name="Parent Task",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )

    class Meta(BaseItemMixin.Meta):
        constraints = [models.UniqueConstraint(fields=["task", "title"], name="unique_task_title")]