from django.db import models


class TimestampMixin(models.Model):

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Created at", help_text="The date and time when the record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Updated at", help_text="The date and time when the record was last modified."
    )

    class Meta:
        abstract = True
