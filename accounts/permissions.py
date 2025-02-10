from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated
from http import HTTPMethod


class DenyAll(BasePermission):
    """
    Custom permission to deny access to all users.
    """

    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False


class CurrentUser(IsAuthenticated):
    """
    Custom permission to only allow users to `retrieve` or `update` their own profile.
    Deleting users is not allowed for anyone.
    """

    def has_object_permission(self, request, view, obj):

        # Deny `DELETE` requests.
        if request.method == HTTPMethod.DELETE:
            return False

        user = request.user
        return obj.pk == user.pk
