from django.db import models
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
        return (
            self.filter(Q(assigned_to__id=user_id) | Q(subtasks__assigned_to__id=user_id))
            .annotate(non_done_subtasks=Count("subtasks", filter=~Q(subtasks__status=self.model.Status_Choices.DONE)))
            .filter(Q(non_done_subtasks__gt=0) | Q(subtasks__isnull=True))
            .distinct()
        )


class SubtaskManager(BaseItemManager):
    pass
