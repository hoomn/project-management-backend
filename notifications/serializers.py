from rest_framework import serializers

from notifications.models import *
from pm.utils import get_activity_description


class NotificationSerializer(serializers.ModelSerializer):

    content_type = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    def get_content_type(self, obj):
        return obj.get_related_verbose_name()

    def get_action(self, obj):
        return obj.content_object.get_action_display()

    def get_description(self, obj):
        return get_activity_description(obj.content_object)

    def get_url(self, obj):
        return obj.get_related_url()

    class Meta:
        model = Notification
        fields = [
            "id",
            "content_type",
            "action",
            "description",
            "url",
            "viewed",
            "created_at",
            "time_since_creation",
        ]
