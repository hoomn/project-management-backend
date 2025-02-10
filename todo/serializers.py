from rest_framework.serializers import ModelSerializer


from .models import Todo


class TodoSerializer(ModelSerializer):

    class Meta:
        model = Todo
        fields = ["id", "description", "due_date", "created_at", "completed", "created_by"]
        read_only_fields = ["created_at", "created_by"]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
