from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Todo


@admin.register(Todo)
class TodoAdmin(ModelAdmin):
    list_display = ("created_by", "description", "completed", "created_at")

    def save_model(self, request, obj, form, change):
        if not change:
            # Only set created_by during the creation.
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
