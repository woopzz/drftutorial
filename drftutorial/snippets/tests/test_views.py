from rest_framework import status as httpstatus
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from drftutorial.snippets.models import Snippet
from drftutorial.snippets.serializers import UserSerializer, SnippetSerializer
from .common import Common


class TestUserViewSet(Common, APITestCase):

    def test_should_return_list_of_users(self):
        first_user = self.create_user(username='first')
        second_user = self.create_user(username='second')

        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)

        data = response.data
        self.assertEqual(data['count'], 2)
        self.assertEqual(
            data['results'],
            UserSerializer([first_user, second_user], many=True, context={'request': response.wsgi_request}).data,
        )

    def test_should_return_user_details(self):
        user = self.create_user()

        response = self.client.get(reverse('user-detail', args=(user.id,)))
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)

        self.assertEqual(
            response.data,
            UserSerializer(user, context={'request': response.wsgi_request}).data,
        )


class TestSnippetViewSet(Common, APITestCase):

    def test_should_return_list_of_snippets(self):
        owner = self.create_user()
        first_snippet = self.create_snippet(owner=owner)
        second_snippet = self.create_snippet(owner=owner)

        response = self.client.get(reverse('snippet-list'))
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)

        data = response.data
        self.assertEqual(data['count'], 2)
        self.assertEqual(
            data['results'],
            SnippetSerializer(
                instance=[first_snippet, second_snippet],
                many=True,
                context={'request': response.wsgi_request}
            ).data,
        )

    def test_should_return_snippet_details(self):
        owner = self.create_user()
        snippet = self.create_snippet(owner=owner, title='title', code='code')

        response = self.client.get(reverse('snippet-detail', args=(snippet.id,)))
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)

        self.assertEqual(
            response.data,
            SnippetSerializer(snippet, context={'request': response.wsgi_request}).data,
        )

    def test_should_create_new_snippet(self):
        user = self.create_user()
        data = {'title': 'some title', 'code': 'some code', 'language': 'perl', 'style': 'vim'}

        self.client.force_login(user)
        response = self.client.post(reverse('snippet-list'), data=data)
        self.assertEqual(response.status_code, httpstatus.HTTP_201_CREATED)

        snippet_id = response.data['id']
        snippet = Snippet.objects.get(pk=snippet_id)
        self.assertEqual(snippet.title, data['title'])
        self.assertEqual(snippet.code, data['code'])
        self.assertEqual(snippet.language, data['language'])
        self.assertEqual(snippet.style, data['style'])
        self.assertEqual(snippet.owner, user)

    def test_should_replace_snippet(self):
        owner = self.create_user()
        snippet = Snippet.objects.create(code='code', owner=owner)

        self.client.force_login(owner)
        response = self.client.put(reverse('snippet-detail', args=(snippet.id,)), data={'code': 'new code'})
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)

        data = response.data
        self.assertEqual(data['id'], snippet.id)
        self.assertEqual(data['code'], 'new code')

        snippet.refresh_from_db()
        self.assertEqual(snippet.code, 'new code')

    def test_should_delete_snippet(self):
        owner = self.create_user()
        snippet = Snippet.objects.create(code='code', owner=owner)

        self.client.force_login(owner)
        response = self.client.delete(reverse('snippet-detail', args=(snippet.id,)))
        self.assertEqual(response.status_code, httpstatus.HTTP_204_NO_CONTENT)

        with self.assertRaises(snippet.DoesNotExist):
            snippet.refresh_from_db()

    def test_should_forbid_anon_user_to_create_new_snippet(self):
        response = self.client.post(reverse('snippet-list'), data={'code': 'stub'})
        self.assertEqual(response.status_code, httpstatus.HTTP_403_FORBIDDEN)

    def test_should_forbid_not_owner_to_manipulate_snippet(self):
        owner = self.create_user(username='owner')
        snippet = Snippet.objects.create(code='owner code', owner=owner)

        another_user = self.create_user(username='another user')
        self.client.force_login(another_user)

        self.assertEqual(
            self.client.put(reverse('snippet-detail', args=(snippet.id,)), data={'code': 'its mine'}).status_code,
            httpstatus.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.delete(reverse('snippet-detail', args=(snippet.id,))).status_code,
            httpstatus.HTTP_403_FORBIDDEN,
        )
