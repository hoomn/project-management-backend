from django.contrib import admin
from unfold.admin import ModelAdmin

from accounts.models import User, AccessList, SingleUseCode


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
        ("Personal info", {"fields": ("first_name", "last_name")}),
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


@admin.register(AccessList)
class AccessListAdmin(ModelAdmin):

    list_display = ("email", "is_active", "created_by", "created_at", "updated_at")
    readonly_fields = ("created_by",)

    def save_model(self, request, obj, form, change):
        if not change:
            # Only set created_by during the creation.
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SingleUseCode)
class SingleUseCodeAdmin(ModelAdmin):

    list_display = ("user", "__str__", "expires_at", "is_used")
    exclude = ("code",)

    def has_add_permission(self, request):
        # Disable the ability to add new single-use code
        return False

    def has_change_permission(self, request, obj=None):
        # Disable the ability to update single-use code
        return False
