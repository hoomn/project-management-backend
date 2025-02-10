from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.mixins import UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .serializers import NotificationSerializer
from .models import Notification


class NotificationViewSet(UpdateModelMixin, ReadOnlyModelViewSet):
    """
    A viewset that provides `list`, `retrieve`, and `update` actions
    for notifications belonging to the current user.
    """

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        current_user = self.request.user
        return Notification.objects.filter(user=current_user, viewed=False)

    @action(detail=False, methods=["POST"])
    def mark_all_as_viewed(self, request):
        self.get_queryset().update(viewed=True)
        return Response({"message": "All notifications marked as viewed."}, status=status.HTTP_200_OK)
