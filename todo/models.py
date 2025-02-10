from django.db import models
from django.contrib.auth import get_user_model

from core.mixins import TimestampMixin

User = get_user_model()


class Todo(TimestampMixin):

    description = models.CharField(max_length=200)
    due_date = models.DateTimeField(verbose_name="expected completion time", blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        verbose_name="created by",
        blank=True,
        null=True,
        related_name="%(class)s_created_by",
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ["due_date", "-created_at"]

    def __str__(self):
        return self.description[:50]
