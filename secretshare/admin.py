from django.contrib import admin
from unfold.admin import ModelAdmin
from django.urls import reverse
from django.utils.html import format_html

from .models import Secret


@admin.register(Secret)
class SecretAdmin(ModelAdmin):
    list_display = ("id", "created_at", "expires_at", "viewed_at", "is_expired")
    readonly_fields = ("id", "created_at", "viewed_at", "share_link")

    def get_fields(self, request, obj=None):
        if obj:
            return ("share_link", "content", "expires_at", "created_at", "viewed_at")
        return ("content", "expires_at")

    def get_readonly_fields(self, request, obj=None):
        if obj:  # lock content after creation so it can't be edited/re-shared
            return self.readonly_fields + ("content",)
        return ("share_link",)

    def share_link(self, obj):
        if not obj or not obj.pk:
            return "(save first to generate link)"
        url = reverse("secretshare:secret-detail", args=[obj.pk])
        return format_html('<a href="{0}" target="_blank">{0}</a>', url)

    share_link.short_description = "Share link"
