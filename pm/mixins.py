from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from django.apps import apps
from django.utils import timezone

from core.mixins import TimestampMixin
from core.utils import get_timesince, get_local_time

from .managers import BaseItemManager

from uuid import uuid4

USER = settings.AUTH_USER_MODEL


class BaseItemMixin(TimestampMixin):
    """
    Common fields for projects, tasks, and subtasks models
    """

    class Priority_Choices(models.IntegerChoices):
        """
        Priority Choices for Project, Task, and Subtask
        """

        CRITICAL = 6, "Critical"
        HIGH = 5, "High"
        UPPER_MEDIUM = 4, "Upper Medium"
        MEDIUM = 3, "Medium"
        LOWER_MEDIUM = 2, "Lower Medium"
        LOW = 1, "Low"

    class Status_Choices(models.IntegerChoices):
        """
        Status Choices for Project, Task, and Subtask
        """

        DONE = 1, "Done"
        READY = 2, "Ready"
        ON_TRACK = 3, "On Track"
        OFF_TRACK = 4, "Off Track"
        ON_HOLD = 5, "On Hold"
        NOT_STARTED = 6, "Not Started"

    uuid = models.UUIDField(unique=True, editable=False, default=uuid4)
    title = models.CharField(verbose_name="Title", max_length=128)
    description = models.TextField(verbose_name="Description", blank=True, null=True)
    start_date = models.DateField(verbose_name="Start Date", blank=True, null=True)
    end_date = models.DateField(verbose_name="End Date", blank=True, null=True)
    status = models.PositiveSmallIntegerField(
        verbose_name="Status",
        choices=Status_Choices,
        default=Status_Choices.NOT_STARTED,
    )
    priority = models.PositiveSmallIntegerField(
        verbose_name="Priority",
        choices=Priority_Choices,
        default=Priority_Choices.MEDIUM,
    )
    is_archived = models.BooleanField(verbose_name="Has been archived", default=False)
    assigned_to = models.ManyToManyField(
        USER,
        verbose_name="Assigned to",
        blank=True,
        related_name="%(class)s_assigned_to",
    )
    created_by = models.ForeignKey(
        USER,
        verbose_name="Created by",
        blank=True,
        null=True,
        related_name="%(class)s_created_by",
        on_delete=models.SET_NULL,
    )
    attachments = GenericRelation("pm.attachment")
    comments = GenericRelation("pm.comment")

    objects = BaseItemManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ["-status", models.F("end_date").asc(nulls_last=True), "-priority"]

    def __str__(self):
        return self.title.title()

    @property
    def time_since_creation(self):
        return get_timesince(self.created_at)

    @property
    def time_since_update(self):
        return get_timesince(self.updated_at)

    @property
    def formatted_created_at(self):
        return get_local_time(self.created_at)

    @property
    def formatted_updated_at(self):
        return get_local_time(self.updated_at)

    @property
    def is_overdue(self):
        if self.status == self.Status_Choices.DONE or self.end_date is None:
            return False
        return timezone.localdate() > self.end_date

    def delete(self, *args, **kwargs):
        # Trigger the pre_delete signal
        models.signals.pre_delete.send(sender=self.__class__, instance=self)
        # Archive instead of delete
        self.archive()

    def archive(self):
        self.is_archived = True
        self.save()

    def get_verbose_name(self):
        return self._meta.verbose_name

    def get_class_name(self):
        return self.__class__.__name__

    def get_absolute_url(self):
        if self.is_archived:
            return None
        return f"/{self.get_class_name()}s/{self.id}"

    def get_comment_count(self):
        Comment = apps.get_model("pm", "comment")
        content_type = ContentType.objects.get_for_model(self.__class__)
        return Comment.objects.filter(content_type=content_type, object_id=self.id).count()

    def get_attachment_count(self):
        Attachment = apps.get_model("pm", "attachment")
        content_type = ContentType.objects.get_for_model(self.__class__)
        return Attachment.objects.filter(content_type=content_type, object_id=self.id).count()


class BaseGenericMixin(TimestampMixin):

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"app_label": "pm", "model__in": ("project", "task", "subtask")},
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    created_by = models.ForeignKey(
        USER,
        verbose_name="Created by",
        blank=True,
        null=True,
        related_name="%(class)s_created_by",
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["content_type", "object_id"])]
        ordering = ["created_at"]

    @property
    def time_since_creation(self):
        return get_timesince(self.created_at)

    def get_verbose_name(self):
        return self._meta.verbose_name

    def get_class_name(self):
        return self.__class__.__name__

    def get_absolute_url(self):
        if self.content_object:
            related_obj = self.content_object
            if hasattr(related_obj, "get_absolute_url"):
                return related_obj.get_absolute_url()
        return None
