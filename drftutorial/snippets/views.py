from django.contrib.auth.models import User
from rest_framework import permissions, renderers, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from snippets.models import Snippet
from snippets.serializers import SnippetSerializer, UserSerializer
from snippets.permissions import IsOwnerOrReadOnly


class SnippetViewSet(viewsets.ModelViewSet):
    serializer_class = SnippetSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]

    @action(
        detail=True,
        renderer_classes=[renderers.StaticHTMLRenderer],
    )
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def get_queryset(self):
        return (
            Snippet.objects.all()
            .select_related('owner')
        )

    def perform_create(self, serializer):
        owner = self.request.user
        serializer.save(owner=owner)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
