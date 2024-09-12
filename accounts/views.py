from django.contrib.auth import authenticate, login
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.mixins import UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, AccessList, SingleUseCode
from accounts.serializers import BasicUserSerializer, UserSerializer

from http import HTTPMethod


class IsSelf(IsAuthenticated):
    """
    Custom permission to only allow users to `retrieve` or `update` their own profile.
    Deleting users is not allowed for anyone.
    """

    def has_object_permission(self, request, view, obj):
        # Deny `DELETE` requests.
        if request.method == HTTPMethod.DELETE:
            return False

        # Allow the user to `retrieve` or `update` their own profile.
        return obj == request.user


class UserViewSet(UpdateModelMixin, ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ("request_single_use_code", "verify_single_use_code"):
            permission_classes = [AllowAny]
        elif self.action == "list":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsSelf]
        return [permission() for permission in permission_classes]

    def list(self, request):
        queryset = User.objects.all()
        serializer = BasicUserSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=[HTTPMethod.POST])
    def request_single_use_code(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "No email provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

        email = email.lower()

        if AccessList.objects.filter(email=email).exists():
            user, created = User.objects.get_or_create(email=email)
            if created:
                # Mark the user as having no password set
                user.set_unusable_password()
                user.save()

            # Check if a code was created for this user in the last 15 minutes
            try:
                # Attempt to get the single use code for the user
                recent_code = SingleUseCode.objects.get(user=user)

                if recent_code.is_valid():
                    return Response(
                        {"error": "Rate limit exceeded. Please try again in a few minutes."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )
            except SingleUseCode.DoesNotExist:
                pass

            SingleUseCode.objects.create(user=user)

        # Always return HTTP 200, regardless of whether the provided email is valid or not.
        return Response(
            {"message": "If we have your email address on file, you will receive a single-use code shortly."},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=[HTTPMethod.POST])
    def verify_single_use_code(self, request):

        code = request.data.get("code")
        if not code:
            return Response({"error": "No Code provided."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, code=code)
        if not user:
            return Response(
                {"error": "The provided code is invalid or has expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # This will create a session for the user
        login(request, user)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )
