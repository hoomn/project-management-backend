from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.module_loading import import_string
from django.forms.models import model_to_dict
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django.conf import settings
from django.apps import apps
from django.utils import timezone

from core.mixins import TimestampMixin
from core.utils import get_timesince, get_local_time

from .managers import BaseItemManager
from .utils import get_change_message

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
        return Comment.objects.filter(
            content_type=content_type, object_id=self.id
        ).count()

    def get_attachment_count(self):
        Attachment = apps.get_model("pm", "attachment")
        content_type = ContentType.objects.get_for_model(self.__class__)
        return Attachment.objects.filter(
            content_type=content_type, object_id=self.id
        ).count()


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


class LoggingMixin:
    """
    A mixin for Django REST Framework ViewSets that automatically logs changes
    made during update operations. It tracks which fields were modified and
    creates an Activity for each update.
    """

    def get_activity_model(self):
        return apps.get_model("pm", "activity")

    def get_activity_serializer(self):
        return import_string("pm.serializers.ActivitySerializer")

    def get_comment_model(self):
        return apps.get_model("pm", "comment")

    def get_comment_serializer(self):
        return import_string("pm.serializers.CommentSerializer")

    def get_attachment_model(self):
        return apps.get_model("pm", "attachment")

    def get_attachment_serializer(self):
        return import_string("pm.serializers.AttachmentSerializer")

    def get_notification_model(self):
        return apps.get_model("notifications", "notification")

    @action(detail=True, methods=["get"])
    def activities(self, request, pk=None):

        Activity = self.get_activity_model()
        ActivitySerializer = self.get_activity_serializer()

        instance = self.get_object()
        content_type = ContentType.objects.get_for_model(instance)

        if request.method == "GET":
            activities = Activity.objects.filter(
                content_type=content_type, object_id=instance.id
            )
            serializer = ActivitySerializer(activities, many=True)
            return Response(serializer.data)

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):

        Comment = self.get_comment_model()
        CommentSerializer = self.get_comment_serializer()

        instance = self.get_object()
        content_type = ContentType.objects.get_for_model(instance)

        if request.method == "GET":
            comments = Comment.objects.filter(
                content_type=content_type, object_id=instance.id
            )
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                comment = serializer.save(
                    content_type=content_type,
                    object_id=instance.id,
                    created_by=request.user,
                )

                change_message = [
                    {
                        "field": "comments",
                        "verbose_name": "Comments",
                        "old_value": [],
                        "new_value": [str(comment)],
                    }
                ]
                self.log_change(self.request, instance, change_message)

                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

    @action(detail=True, methods=["get", "post"])
    def attachments(self, request, pk=None):

        Attachment = self.get_attachment_model()
        AttachmentSerializer = self.get_attachment_serializer()

        instance = self.get_object()
        content_type = ContentType.objects.get_for_model(instance)

        if request.method == "GET":
            attachments = Attachment.objects.filter(
                content_type=content_type, object_id=instance.id
            )
            serializer = AttachmentSerializer(attachments, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            serializer = AttachmentSerializer(data=request.data)
            if serializer.is_valid():
                attachment = serializer.save(
                    content_type=content_type,
                    object_id=instance.id,
                    created_by=request.user,
                )

                change_message = [
                    {
                        "field": "attachments",
                        "verbose_name": "Attachments",
                        "old_value": [],
                        "new_value": [str(attachment)],
                    }
                ]
                self.log_change(self.request, instance, change_message)

                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

    def log_addition(self, request, instance):

        Activity = self.get_activity_model()
        Notification = self.get_notification_model()

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

        Activity = self.get_activity_model()
        Notification = self.get_notification_model()

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
        self.log_addition(self.request, instance)

    def perform_update(self, serializer):

        # Get the instance before the update
        instance = self.get_object()
        data_before_update = model_to_dict(instance)

        # Perform the update
        serializer.save()

        # Get the instance after the update
        instance = self.get_object()
        change_message = get_change_message(instance, data_before_update)

        if change_message:
            self.log_change(self.request, instance, change_message)

    def perform_destroy(self, instance):
        self.log_deletion(self.request, instance)

        if instance.__class__.__name__ in ("Project", "Task", "Subtask"):
            # Archive if instance is a Project, Task, or Subtask
            instance.archive()

        if instance.__class__.__name__ in ("Comment", "Attachment"):
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
