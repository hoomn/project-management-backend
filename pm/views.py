from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from django_filters import rest_framework as filters

from .mixins import LoggingMixin
from .models import Domain, Priority, Status, Project, Task, Subtask
from .models import Comment, Attachment, Activity

from .permissions import IsOwnerOrReadOnly

from .serializers import DomainDropdownSerializer, PriorityDropdownSerializer, StatusDropdownSerializer
from .serializers import ProjectSerializer, TaskSerializer, SubtaskSerializer
from .serializers import CommentSerializer, AttachmentSerializer, ActivitySerializer


class DomainDropdownViewSet(ReadOnlyModelViewSet):

    queryset = Domain.objects.all()
    serializer_class = DomainDropdownSerializer
    permission_classes = [IsAuthenticated]


class ProjectDropdownViewSet(ReadOnlyModelViewSet):

    queryset = Project.objects.all()
    serializer_class = DomainDropdownSerializer
    permission_classes = [IsAuthenticated]


class TaskDropdownViewSet(ReadOnlyModelViewSet):

    queryset = Task.objects.all()
    serializer_class = DomainDropdownSerializer
    permission_classes = [IsAuthenticated]


class PriorityDropdownViewSet(ReadOnlyModelViewSet):

    queryset = Priority.objects.all()
    serializer_class = PriorityDropdownSerializer
    permission_classes = [IsAuthenticated]


class StatusDropdownViewSet(ReadOnlyModelViewSet):

    queryset = Status.objects.all()
    serializer_class = StatusDropdownSerializer
    permission_classes = [IsAuthenticated]


class ProjectFilter(filters.FilterSet):
    """
    FilterSet for Project model
    """

    class Meta:
        model = Project
        fields = ["title", "start_date", "end_date", "status", "priority"]


class ProjectViewSet(LoggingMixin, ModelViewSet):
    """
    ViewSet for handling CRUD operations on Project model instances.
    Incorporates automatic logging of changes during updates via LoggingMixin,
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    # lookup_field = "uuid"

    filterset_class = ProjectFilter
    # Fields that can be searched using ?search=query
    search_fields = ["title", "description"]
    # Default ordering
    ordering = ["-priority", "end_date", "status"]

    def get_queryset(self):
        current_user = self.request.user
        queryset = Project.objects.filter(domain__in=current_user.domain_membership.all())
        return queryset

    @action(detail=True, methods=["get"])
    def tasks(self, request, pk=None):
        project = self.get_object()
        tasks = Task.objects.filter(project=project)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="priority/choices")
    def priority_choices(self, request):
        choices = Project._meta.get_field("priority").choices
        formatted_choices = [{"value": choice[0], "label": choice[1]} for choice in choices]
        return Response(formatted_choices)

    @action(detail=False, methods=["get"], url_path="status/choices")
    def status_choices(self, request):
        choices = Project._meta.get_field("status").choices
        formatted_choices = [{"value": choice[0], "label": choice[1]} for choice in choices]
        return Response(formatted_choices)


class TaskFilter(filters.FilterSet):
    """
    FilterSet for Task model
    """

    User = get_user_model()

    assigned_to = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        null_label="Unassigned",  # Allows filtering for null values
    )

    class Meta:
        model = Task
        fields = ["title", "description", "assigned_to", "status", "priority"]


class TaskViewSet(LoggingMixin, ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["title", "start_date", "end_date", "status", "priority"]
    ordering = ["-priority", "end_date", "status"]

    @action(detail=False, methods=["get"])
    def current_user_domain(self, request):
        # Get all tasks that belong to any of the current user's domains
        user = request.user

        # Get the 'assigned_to' parameter from the URL
        assigned_to = request.query_params.get("assigned_to")
        tasks = Task.objects.filter(project__domain__in=user.domain_membership.all())

        # Further filter by 'assigned_to' of task and subtasks if provided
        if assigned_to:
            tasks = Task.objects.assigned_to_user(assigned_to)

        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def me(self, request):
        # Get tasks assigned to the current user
        user = request.user
        queryset = Task.objects.assigned_to_user(user.id)
        filtered_queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def subtasks(self, request, pk=None):
        task = self.get_object()
        subtasks = Subtask.objects.filter(task=task)
        serializer = SubtaskSerializer(subtasks, many=True)
        return Response(serializer.data)


class SubtaskViewSet(LoggingMixin, ModelViewSet):
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def current_user(self, request):
        # Get subtasks assigned to the current user
        user = request.user
        subtasks = Subtask.objects.filter(assigned_to=user)
        serializer = self.get_serializer(subtasks, many=True)
        return Response(serializer.data)


class CommentViewSet(LoggingMixin, ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        content_type = self.request.query_params.get("content_type")
        object_id = self.request.query_params.get("object_id")

        if self.action == "list":
            if content_type and object_id:
                return queryset.filter(content_type=content_type, object_id=object_id)
            # If content_type or object_id are missing for list action, return an empty queryset
            return Comment.objects.none()

        return queryset


class AttachmentViewSet(LoggingMixin, ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        content_type = self.request.query_params.get("content_type")
        object_id = self.request.query_params.get("object_id")

        if self.action == "list":
            if content_type and object_id:
                return queryset.filter(content_type=content_type, object_id=object_id)
            # If content_type or object_id are missing for list action, return an empty queryset
            return Attachment.objects.none()

        return queryset


class ActivityPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "num_pages": self.page.paginator.num_pages,
                "number": self.page.number,
                "next": self.page.next_page_number() if self.page.has_next() else None,
                "previous": self.page.previous_page_number() if self.page.has_previous() else None,
                "results": data,
            }
        )


class ActivityViewSet(ReadOnlyModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ActivityPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        content_type = self.request.query_params.get("content_type")
        object_id = self.request.query_params.get("object_id")
        if content_type and object_id:
            queryset = queryset.filter(content_type=content_type, object_id=object_id)
        return queryset

    def paginate_queryset(self, queryset):
        content_type = self.request.query_params.get("content_type")
        object_id = self.request.query_params.get("object_id")

        # Skip pagination if content_type and object_id are present
        if content_type and object_id:
            return None

        # Otherwise, paginate as usual
        return super().paginate_queryset(queryset)
