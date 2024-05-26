import datetime as dt

from django.contrib.auth.models import User
from rest_framework import serializers

from drftutorial.snippets.models import Snippet


class TimestampField(serializers.IntegerField):
    default_error_messages = {
        'timestamp_must_be_int': 'A timestamp value must be integer.',
        'invalid_timestamp': 'A timestamp value seems to be invalid.',
    }

    def to_representation(self, value):
        if isinstance(value, dt.datetime):
            return value.timestamp()

        return None

    def to_internal_value(self, data):
        if not isinstance(data, int):
            self.fail('timestamp_must_be_int')

        try:
            return dt.datetime.fromtimestamp(data)
        except ValueError:
            self.fail('invalid_timestamp')


class SnippetSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    expired_at_timestamp = TimestampField(source='expired_at', required=False, allow_null=True)

    class Meta:
        model = Snippet
        fields = [
            'id', 'owner', 'title', 'code', 'linenos',
            'language', 'style', 'expired_at_timestamp',
        ]


class UserSerializer(serializers.ModelSerializer):
    snippets = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'snippets']
