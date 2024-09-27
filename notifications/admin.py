from django.contrib import admin
from unfold.admin import ModelAdmin

from notifications.models import Notification, Category, EmailLog


class ReadOnlyAdmin(ModelAdmin):

    def has_add_permission(self, request):
        # Disable the ability to add new notification
        return False

    def has_change_permission(self, request, obj=None):
        # Disable the ability to update notifications
        return False


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ["user", "viewed", "created_at", "updated_at"]


@admin.register(EmailLog)
class EmailLogAdmin(ReadOnlyAdmin):
    list_display = ["email", "status", "description", "created_at"]


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["content_type", "action"]
