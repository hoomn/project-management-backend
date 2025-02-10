from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from djoser.serializers import UidAndTokenSerializer
from djoser.utils import decode_uid

from accounts.models import User
from accounts.serializers import UserDropdownSerializer


class UserDropdownViewSet(ReadOnlyModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserDropdownSerializer
    permission_classes = [IsAuthenticated]


class TokenValidationViewSet(GenericViewSet):

    permission_classes = [AllowAny]
    token_generator = default_token_generator
    serializer_class = UidAndTokenSerializer

    @action(detail=False, methods=["post"], url_path="password/reset")
    def validate_password_reset_token(self, request):
        """
        Validate the password reset token without actually resetting the password.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="activation")
    def validate_activation_token(self, request):
        """
        Validate the activation token.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        User = get_user_model()

        try:
            # Decode the uid and fetch the user
            uid = decode_uid(validated_data.get("uid", ""))
            user = User.objects.get(pk=uid, is_active=False)

        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_200_OK)
