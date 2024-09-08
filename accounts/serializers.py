from rest_framework import serializers

from accounts.models import User, Profile


class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "initial"]


class UserSerializer(serializers.ModelSerializer):

    domain_membership = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    has_usable_password = serializers.SerializerMethodField()
    notification = serializers.BooleanField(source="profile.notification")

    def get_has_usable_password(self, obj):
        return obj.has_usable_password()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "initial",
            "is_staff",
            "domain_membership",
            "has_usable_password",
            "notification",
        ]
        read_only_fields = ["email", "initial", "is_staff"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        notification = profile_data.get("notification")

        instance = super().update(instance, validated_data)

        if notification is not None:
            Profile.objects.update_or_create(
                user=instance, defaults={"notification": notification}
            )

        return instance
