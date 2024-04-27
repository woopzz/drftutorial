from django.contrib.auth.models import User
from rest_framework import permissions, renderers, viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from drftutorial.snippets.models import Snippet
from drftutorial.snippets.serializers import SnippetSerializer, UserSerializer
from drftutorial.snippets.permissions import IsOwnerOrReadOnly


class SnippetViewSet(viewsets.ModelViewSet):
    serializer_class = SnippetSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['language', 'style', 'owner']
    search_fields = ['title', 'code']
    ordering_fields = ['created']

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

    def get_throttles(self):
        if self.action == 'create':
            self.throttle_scope = 'snippet_create'
        return super().get_throttles()

    def perform_create(self, serializer):
        owner = self.request.user
        serializer.save(owner=owner)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username']
    ordering_fields = ['username']
