from rest_framework import serializers

from .models import Domain, Project, Task, Subtask


class DomainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Domain
        fields = ["id", "title", "members"]


class BaseItemSerializerMixin(serializers.ModelSerializer):
    """
    Mixin to provide common fields and methods for Project, Task, and Subtask serializers.
    """

    comment_count = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()

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
        ]

        # This ensures the field can't be set directly through the API
        read_only_fields = ["created_by"]


class ProjectSerializer(BaseItemSerializerMixin):

    domain_title = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()

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

    subtask_count = serializers.SerializerMethodField()

    def get_subtask_count(self, instance):
        return instance.subtasks.count()

    class Meta(BaseItemSerializerMixin.Meta):
        model = Task
        fields = BaseItemSerializerMixin.Meta.fields + ["project", "subtask_count"]


class SubtaskSerializer(BaseItemSerializerMixin):

    class Meta(BaseItemSerializerMixin.Meta):
        model = Subtask
        fields = BaseItemSerializerMixin.Meta.fields + ["task"]
