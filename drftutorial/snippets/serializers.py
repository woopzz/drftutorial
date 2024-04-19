from django.contrib.auth.models import User
from rest_framework import serializers

from drftutorial.snippets.models import Snippet


class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight')

    class Meta:
        model = Snippet
        fields = [
            'url', 'id', 'highlight', 'owner',
            'title', 'code', 'linenos', 'language', 'style',
        ]


class UserSerializer(serializers.ModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(
        view_name='snippet-detail',
        many=True,
        read_only=True,
    )

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'snippets']
