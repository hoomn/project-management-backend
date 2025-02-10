from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from django.db import models
from django.conf import settings
from django.apps import apps
from django.utils import timezone

from core.mixins import TimestampMixin
from core.utils import get_timesince, get_local_time

from .utils import get_change_message

from uuid import uuid4


User = get_user_model()


class BaseItemMixin(TimestampMixin):
    """
    Common fields for projects, tasks, and subtasks models
    """

    uuid = models.UUIDField(unique=True, editable=False, default=uuid4)
    title = models.CharField(verbose_name="title", max_length=128)
    description = models.TextField(verbose_name="description", blank=True, null=True)
    start_date = models.DateField(verbose_name="start date", blank=True, null=True)
    end_date = models.DateField(verbose_name="end date", blank=True, null=True)
    status = models.ForeignKey(
        to="status",
        verbose_name="status",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    priority = models.ForeignKey(
        to="priority",
        verbose_name="priority",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    is_archived = models.BooleanField(verbose_name="has been archived", default=False)
    assigned_to = models.ManyToManyField(
        User,
        verbose_name="assigned to",
        blank=True,
        related_name="%(class)s_assigned_to",
    )
    created_by = models.ForeignKey(
        User,
        verbose_name="created by",
        blank=True,
        null=True,
        related_name="%(class)s_created_by",
        on_delete=models.SET_NULL,
    )
    attachments = GenericRelation("pm.attachment")
    comments = GenericRelation("pm.comment")

    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ["-status__pk", models.F("end_date").asc(nulls_last=True), "-priority__pk"]

    def __str__(self):
        return self.title.title()

    @property
    def content_type(self):
        content_type = ContentType.objects.get_for_model(self)
        return content_type.id

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
        try:
            Status = apps.get_model("pm", "status")
            done = Status.objects.get(title="Done")
        except:
            return None
        if self.status == done or self.end_date is None:
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
        return f"/{self.get_class_name().lower()}s/{self.id}"

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
        limit_choices_to={
            "app_label": "pm",
            "model__in": ("project", "task", "subtask"),
        },
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    is_updated = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        verbose_name="created by",
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


class LoggingMixin:
    """
    A mixin for Django REST Framework ViewSets that automatically logs changes
    made during update operations. It tracks which fields were modified and
    creates an Activity for each update.
    """

    MAIN_CLASSES = ("Project", "Task", "Subtask")
    GENERIC_CLASSES = ("Comment", "Attachment")

    def get_activity_model(self):
        return apps.get_model("pm", "activity")

    def get_notification_model(self):
        return apps.get_model("notifications", "notification")

    def log_addition(self, request, instance):

        Notification = self.get_notification_model()
        Activity = self.get_activity_model()

        activity = Activity.objects.create(
            action=Activity.Action_Choices.CREATE,
            content=[],
            content_object=instance,
            created_by=request.user,
        )

        # List of users being notified (assigned_to + owner)
        if hasattr(instance, "assigned_to"):
            assigned_users = instance.assigned_to.all()
            assigned_users = set(assigned_users)
        else:
            assigned_users = set()

        assigned_users.add(request.user)

        for user in assigned_users:
            Notification.objects.create(user=user, content_object=activity)

    def log_change(self, request, instance, change_message):

        Notification = self.get_notification_model()
        Activity = self.get_activity_model()

        activity = Activity.objects.create(
            action=Activity.Action_Choices.UPDATE,
            content=change_message,
            content_object=instance,
            created_by=request.user,
        )

        # List of users being notified (assigned_to + owner)
        if hasattr(instance, "assigned_to"):
            assigned_users = instance.assigned_to.all()
            assigned_users = set(assigned_users)
        else:
            assigned_users = set()

        assigned_users.add(instance.created_by)

        for user in assigned_users:
            Notification.objects.create(user=user, content_object=activity)

    def log_deletion(self, request, instance):

        Activity = self.get_activity_model()
        Activity.objects.create(
            action=Activity.Action_Choices.DELETE,
            content=[],
            content_object=instance,
            created_by=request.user,
        )

    def perform_create(self, serializer):
        # Set the created_by field of a project to the current user upon creation.
        instance = serializer.save(created_by=self.request.user)

        if instance.__class__.__name__ in self.MAIN_CLASSES:
            self.log_addition(self.request, instance)

        if instance.__class__.__name__ in self.GENERIC_CLASSES:
            # Access the related instance
            related_instance = instance.content_object
            change_message = [
                {
                    "field": f"{instance.__class__.__name__.lower()}s",
                    "verbose_name": f"{instance.__class__.__name__}s",
                    "old_value": [],
                    "new_value": [str(instance)],
                }
            ]
            self.log_change(self.request, related_instance, change_message)

    def perform_update(self, serializer):

        # Get the instance before the update
        instance = self.get_object()

        if instance.__class__.__name__ in self.MAIN_CLASSES:
            # Get dict representation of instance before update
            data_before_update = model_to_dict(instance)

            # Perform the update
            serializer.save()

            # Get the instance after the update
            instance = self.get_object()

            change_message = get_change_message(instance, data_before_update)

            if change_message:
                self.log_change(self.request, instance, change_message)

        if instance.__class__.__name__ in self.GENERIC_CLASSES:
            # Get string representation of instance before update
            instance_before_update = str(instance)

            # Perform the update
            serializer.save(is_updated=True)

            # Get the instance after the update
            instance = self.get_object()

            # Access the related instance
            related_instance = instance.content_object
            change_message = [
                {
                    "field": f"{instance.__class__.__name__.lower()}s",
                    "verbose_name": f"{instance.__class__.__name__}s",
                    "old_value": [instance_before_update],
                    "new_value": [str(instance)],
                }
            ]
            if instance_before_update != str(instance):
                self.log_change(self.request, related_instance, change_message)

    def perform_destroy(self, instance):

        if instance.__class__.__name__ in self.MAIN_CLASSES:
            # Create a deletion log
            self.log_deletion(self.request, instance)
            # Archive if instance is a Project, Task, or Subtask
            instance.archive()

        if instance.__class__.__name__ in self.GENERIC_CLASSES:
            # Access the related instance (either Project, Task, or Subtask)
            related_instance = instance.content_object
            change_message = [
                {
                    "field": f"{instance.__class__.__name__.lower()}s",
                    "verbose_name": f"{instance.__class__.__name__}s",
                    "old_value": [str(instance)],
                    "new_value": [],
                }
            ]
            self.log_change(self.request, related_instance, change_message)
            # Delete for other types of instances
            instance.delete()
