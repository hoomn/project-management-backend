from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from .models import Todo
from .serializers import TodoSerializer


class TodoViewSet(ModelViewSet):

    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter todos to show only the current user's todos
        return Todo.objects.filter(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_done(self, request, pk=None):
        todo = self.get_object()
        if not todo.completed:
            todo.completed = True
            todo.save()
        return Response(TodoSerializer(todo).data)

    @action(detail=True, methods=["post"])
    def mark_undone(self, request, pk=None):
        todo = self.get_object()
        if todo.completed:
            todo.completed = False
            todo.save()
        return Response(TodoSerializer(todo).data)
