from django.contrib.auth.models import User

from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry

from drftutorial.snippets.models import Snippet


@registry.register_document
class SnippetDocument(Document):
    class Index:
        name = 'snippets'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Snippet
        fields = ['title', 'code']


@registry.register_document
class UserDocument(Document):
    class Index:
        name = 'users'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = User
        fields = ['username']
