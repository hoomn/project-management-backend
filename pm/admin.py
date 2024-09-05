from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import *


@admin.register(Attachment)
class AttachmentAdmin(ModelAdmin):
    list_display = ("file_name", "file_size", "content_type", "created_at", "created_by")

    def save_model(self, request, obj, form, change):
        if not change:
            # Only set created_by during the creation.
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ("text", "content_type", "created_at", "updated_at", "created_by")

    def save_model(self, request, obj, form, change):
        if not change:
            # Only set created_by during the creation.
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Activity)
class ActivityAdmin(ModelAdmin):
    list_display = ("action", "content", "content_type", "object_id", "created_at", "created_by")

    def has_add_permission(self, request):
        # Disable the ability to add new notification
        return False

    def has_change_permission(self, request, obj=None):
        # Disable the ability to update notifications
        return False


@admin.register(Domain)
class AttachmentAdmin(ModelAdmin):
    list_display = ("title", "members_count", "created_at", "created_by")
    filter_horizontal = ("members",)

    def save_model(self, request, obj, form, change):
        if not change:
            # Only set created_by during the creation.
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def members_count(self, obj):
        return obj.members.count()

    members_count.short_description = 'Number of Members'


class ItemModelAdmin(ModelAdmin):
    filter_horizontal = ("assigned_to",)

    def get_queryset(self, request):
        return self.model.all_objects.all()

    def get_list_display(self, request):
        return super().get_list_display(request) + (
            "title",
            "status",
            "priority",
            "is_archived",
            "updated_at",
            "created_by",
        )

    def save_model(self, request, obj, form, change):
        if not change:
            # Only set created_by during the creation.
            obj.created_by = request.user
        super().save_model(request, obj, form, change)



@admin.register(Project)
class ProjectAdmin(ItemModelAdmin):
    list_display = ("domain",)


@admin.register(Task)
class TaskAdmin(ItemModelAdmin):
    list_display = ("project",)


@admin.register(Subtask)
class SubtaskAdmin(ItemModelAdmin):
    list_display = ("task",)