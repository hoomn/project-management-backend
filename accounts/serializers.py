from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from djoser.serializers import UserSerializer as DjoserUserSerializer
from djoser.serializers import SendEmailResetSerializer

from accounts.models import User
from core.mixins import DropdownModelSerializer

from .utils import validate_recaptcha


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    recaptcha = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):

        # Remove recaptcha from attrs and validate
        recaptcha_token = attrs.pop("recaptcha", None)
        validate_recaptcha(recaptcha_token)

        # Validate credentials using parent class
        return super().validate(attrs)


class UserDropdownSerializer(DropdownModelSerializer):

    class Meta:
        model = User


class CustomUserSerializer(DjoserUserSerializer):

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + ("first_name", "last_name", "initials", "email_notification")


class CustomSendEmailResetSerializer(SendEmailResetSerializer):

    recaptcha = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):

        # Remove recaptcha from attrs and validate
        recaptcha_token = attrs.pop("recaptcha", None)
        validate_recaptcha(recaptcha_token)

        return super().validate(attrs)
