from django.db import models
from rest_framework import serializers


class TimestampMixin(models.Model):

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Created at", help_text="The date and time when the record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Updated at", help_text="The date and time when the record was last modified."
    )

    class Meta:
        abstract = True


class DropdownModelSerializer(serializers.ModelSerializer):
    """
    Base serializer for model-based dropdowns.
    Automatically configures fields for dropdown usage.
    Override `get_value` and `get_label` methods to customize dropdown options.

    For example:
    ```
    class UserDropdownSerializer(DropdownModelSerializer):
        class Meta:
            model = User

        def get_label(self, instance):
            return f"{instance.name} ({instance.email})"

    ```
    """

    value = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override Meta fields to ensure only value and label are returned
        self.Meta.fields = ("value", "label")

    def get_value(self, instance):
        """Return the value to be used when option is selected"""
        return instance.id

    def get_label(self, instance):
        """Return the label to be displayed in dropdown"""
        return str(instance)
