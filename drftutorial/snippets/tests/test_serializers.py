import datetime as dt

from drftutorial.snippets.serializers import UserSerializer, SnippetSerializer
from .common import Common


class TestUserSerializer(Common):

    def test_should_convert_objects_to_data(self):
        first_user = self.create_user(username='first')
        second_user = self.create_user(username='second')

        first_user_snippet_1 = self.create_snippet(owner=first_user)
        first_user_snippet_2 = self.create_snippet(owner=first_user)
        second_user_snippet_1 = self.create_snippet(owner=second_user)

        self.assertEqual(
            UserSerializer([first_user, second_user], many=True, context={'request': None}).data,
            [{
                'id': first_user.id,
                'username': first_user.username,
                'snippets': [
                    first_user_snippet_1.id,
                    first_user_snippet_2.id,
                ],
            }, {
                'id': second_user.id,
                'username': second_user.username,
                'snippets': [
                    second_user_snippet_1.id,
                ],
            }]
        )


class TestSnippetSerializer(Common):

    def test_should_convert_objects_to_data(self):
        owner = self.create_user()
        first_snippet = self.create_snippet(
            owner=owner,
            title='first snippet title',
            code='first snippet code',
            linenos=True,
            language='c',
            style='vim',
            expired_at=dt.datetime.now() + dt.timedelta(days=10),
        )
        second_snippet = self.create_snippet(
            owner=owner,
            title='second snippet title',
            code='second snippet code',
            linenos=False,
            language='python',
            style='dracula',
            expired_at=dt.datetime.now() + dt.timedelta(days=20),
        )
        self.assertEqual(
            SnippetSerializer([first_snippet, second_snippet], many=True, context={'request': None}).data,
            [
                {
                    'id': snippet.id,
                    'owner': owner.username,
                    'title': snippet.title,
                    'code': snippet.code,
                    'linenos': snippet.linenos,
                    'language': snippet.language,
                    'style': snippet.style,
                    'expired_at_timestamp': snippet.expired_at.timestamp(),
                }
                for snippet in (first_snippet, second_snippet)
            ],
        )

    def test_should_convert_data_to_object(self):
        data = {
            'title': 'test title',
            'code': '123',
            'linenos': True,
            'language': 'c',
            'style': 'vim',
        }
        serializer = SnippetSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        owner = self.create_user()
        snippet = serializer.save(owner=owner)
        self.assertEqual(snippet.title, data['title'])
        self.assertEqual(snippet.code, data['code'])
        self.assertEqual(snippet.linenos, data['linenos'])
        self.assertEqual(snippet.language, data['language'])
        self.assertEqual(snippet.style, data['style'])
        self.assertEqual(snippet.owner, owner)
