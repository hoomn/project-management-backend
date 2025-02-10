from django.db import models
from django.apps import apps
from django.db.models import Q, Count


class BaseItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)


class ProjectManager(BaseItemManager):
    pass


class TaskManager(BaseItemManager):

    # TODO: This method needs improvements
    def assigned_to_user(self, user_id):
        """
        Get tasks directly assigned to the user
        +
        Get tasks with subtasks assigned to the user and not done
        """
        # Try to get DONE status ID, fallback to None if table is empty
        try:
            Status = apps.get_model("pm", "status")
            done_status_id = Status.objects.get(title="DONE").id
        except Status.DoesNotExist:
            # If status table is empty, return all tasks for the user
            return self.filter(Q(assigned_to__id=user_id) | Q(subtasks__assigned_to__id=user_id)).distinct()

        # If we have a done_status_id, proceed with the full query
        return (
            self.filter(Q(assigned_to__id=user_id) | Q(subtasks__assigned_to__id=user_id))
            .annotate(non_done_subtasks=Count("subtasks", filter=~Q(subtasks__status_id=done_status_id)))
            .filter(Q(non_done_subtasks__gt=0) | Q(subtasks__isnull=True))
            .distinct()
        )


class SubtaskManager(BaseItemManager):
    pass
