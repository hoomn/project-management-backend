from django.template.defaultfilters import filesizeformat

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .models import Domain, Project, Task, Subtask
from .models import Comment, Attachment, Activity

from .utils import get_activity_description, file_type_validator


class DomainSerializer(ModelSerializer):

    class Meta:
        model = Domain
        fields = ["id", "title", "members"]


class BaseItemSerializerMixin(ModelSerializer):
    """
    Mixin to provide common fields and methods for Project, Task, and Subtask
    """

    comment_count = SerializerMethodField()
    attachment_count = SerializerMethodField()

    def get_comment_count(self, instance):
        return instance.get_comment_count()

    def get_attachment_count(self, instance):
        return instance.get_attachment_count()

    class Meta:
        fields = [
            "id",
            "uuid",
            "title",
            "description",
            "start_date",
            "end_date",
            "status",
            "get_status_display",
            "priority",
            "get_priority_display",
            "assigned_to",
            "created_by",
            "time_since_creation",
            "time_since_update",
            "is_overdue",
            "comment_count",
            "attachment_count",
            "content_type",
        ]

        # This ensures the field can't be set directly through the API
        read_only_fields = ["created_by", "content_type"]


class ProjectSerializer(BaseItemSerializerMixin):

    domain_title = SerializerMethodField()
    task_count = SerializerMethodField()

    def get_domain_title(self, instance):
        return instance.domain.title

    def get_task_count(self, instance):
        return instance.tasks.count()

    class Meta(BaseItemSerializerMixin.Meta):
        model = Project
        fields = BaseItemSerializerMixin.Meta.fields + [
            "domain",
            "domain_title",
            "task_count",
        ]


class TaskSerializer(BaseItemSerializerMixin):

    subtask_count = SerializerMethodField()

    def get_subtask_count(self, instance):
        return instance.subtasks.count()

    class Meta(BaseItemSerializerMixin.Meta):
        model = Task
        fields = BaseItemSerializerMixin.Meta.fields + ["project", "subtask_count"]


class SubtaskSerializer(BaseItemSerializerMixin):

    class Meta(BaseItemSerializerMixin.Meta):
        model = Subtask
        fields = BaseItemSerializerMixin.Meta.fields + ["task"]


class CommentSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = [
            "id",
            "text",
            "content_type",
            "object_id",
            "created_by",
            "created_at",
            "updated_at",
            "time_since_creation",
            "is_updated",
        ]


class AttachmentSerializer(ModelSerializer):

    extension = SerializerMethodField()
    file_size = SerializerMethodField()

    def validate_file(self, value):
        file_type_validator(value)
        return value

    def get_extension(self, instance):
        return instance.extension

    def get_file_size(self, instance):
        return filesizeformat(instance.file_size)

    class Meta:
        model = Attachment
        fields = [
            "id",
            "file",
            "file_name",
            "extension",
            "file_size",
            "description",
            "content_type",
            "object_id",
            "created_by",
            "created_at",
            "time_since_creation",
            "is_updated",
        ]


class ActivitySerializer(ModelSerializer):
    content_type = SerializerMethodField()
    description = SerializerMethodField()

    def get_content_type(self, obj):
        return obj.content_type.model if obj.content_type else None

    def get_description(self, obj):
        return get_activity_description(obj)

    class Meta:
        model = Activity
        fields = ["id", "get_action_display", "content_type", "description", "created_by", "time_since_creation"]
