from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import SAFE_METHODS


class IsOwnerOrReadOnly(IsAuthenticated):
    """
    Custom permission to allow only the owner of an object to `update` or `delete` it.
    All authenticated users are allowed to `retrieve` objects (GET, HEAD, OPTIONS requests).
    """

    def has_object_permission(self, request, view, obj):
        # Allow read-only access for SAFE_METHODS (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True

        # Allow write access only if the user is the object owner
        return obj.created_by == request.user
