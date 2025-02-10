from django.contrib import admin
from unfold.admin import ModelAdmin

from accounts.models import User


@admin.register(User)
class UserAdmin(ModelAdmin):

    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "last_login",
        "created_at",
    )
    filter_horizontal = ("groups", "user_permissions")
    search_fields = ("email",)
    ordering = ("email",)

    fieldsets = [
        ("Credentials", {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email_notification")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    ]
