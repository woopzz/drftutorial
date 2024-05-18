from django.contrib.auth.models import User

from rest_framework import permissions, renderers, viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from elasticsearch_dsl import Q

from drftutorial.snippets.models import Snippet
from drftutorial.snippets.serializers import SnippetSerializer, UserSerializer
from drftutorial.snippets.permissions import IsOwnerOrReadOnly
from drftutorial.snippets.filters import ElasticSeachFilter
from drftutorial.snippets.documents import SnippetDocument, UserDocument

EnhancedTokenObtainPairView = extend_schema_view(
    post=extend_schema(summary='Create a new JWT and a refresh token for it.', tags=['Tokens']),
)(TokenObtainPairView)

EnhancedTokenRefreshView = extend_schema_view(
    post=extend_schema(summary='Obtain a new pair of tokens by refresh token.', tags=['Tokens']),
)(TokenRefreshView)


@extend_schema_view(
    list=extend_schema(summary='Get list of snippets.', tags=['Snippets']),
    create=extend_schema(summary='Create a new snippet.', tags=['Snippets']),
    retrieve=extend_schema(summary='Get info of a particular snippet.', tags=['Snippets']),
    update=extend_schema(summary='Replace info of a particular snippet.', tags=['Snippets']),
    partial_update=extend_schema(summary='Update some info of a particular snippet.', tags=['Snippets']),
    destroy=extend_schema(summary='Delete a particular snippet.', tags=['Snippets']),

    highlight=extend_schema(summary='Get an HTML page with prettified code.', tags=['Snippets (extra)']),
)
class SnippetViewSet(viewsets.ModelViewSet):
    serializer_class = SnippetSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]
    filter_backends = [ElasticSeachFilter, DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['language', 'style', 'owner']
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

    def get_elastic_search_query(self, search_term):
        search_fields = ['title', 'code']
        q = Q('multi_match', query=search_term, fields=search_fields, fuzziness='auto')
        return SnippetDocument.search().query(q)

    def perform_create(self, serializer):
        owner = self.request.user
        serializer.save(owner=owner)


@extend_schema_view(
    list=extend_schema(summary='Get list of users.', tags=['Users']),
    retrieve=extend_schema(summary='Get info of a particular user.', tags=['Users']),
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    filter_backends = [ElasticSeachFilter, filters.OrderingFilter]
    ordering_fields = ['username']

    def get_elastic_search_query(self, search_term):
        return UserDocument.search().query('match', username=search_term)
