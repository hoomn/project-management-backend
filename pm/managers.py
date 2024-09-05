from django.db import models


class BaseItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)
