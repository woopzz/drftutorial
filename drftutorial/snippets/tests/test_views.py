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

    def test_should_order_by_username(self):
        anna = self.create_user(username='Anna')
        zac = self.create_user(username='Zac')

        response = self.client.get(reverse('user-list'), data={'ordering': 'username'})
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)
        self.assertEqual(
            response.data['results'],
            UserSerializer([anna, zac], many=True, context={'request': response.wsgi_request}).data,
        )

        response = self.client.get(reverse('user-list'), data={'ordering': '-username'})
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)
        self.assertEqual(
            response.data['results'],
            UserSerializer([zac, anna], many=True, context={'request': response.wsgi_request}).data,
        )

    def test_should_search_by_username(self):
        john = self.create_user(username='John')
        jonathan = self.create_user(username='Jonathan')

        response = self.client.get(reverse('user-list'), data={'search': 'abc'})
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])

        response = self.client.get(reverse('user-list'), data={'search': 'joh'})
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'],
            UserSerializer([john], many=True, context={'request': response.wsgi_request}).data,
        )

        response = self.client.get(reverse('user-list'), data={'search': 'jo'})
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(
            response.data['results'],
            UserSerializer([john, jonathan], many=True, context={'request': response.wsgi_request}).data,
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

    def test_should_order_by_created(self):
        owner = self.create_user()
        first_snippet = self.create_snippet(owner=owner)
        second_snippet = self.create_snippet(owner=owner)

        response = self.client.get(reverse('snippet-list'), data={'ordering': 'created'})
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)
        self.assertEqual(
            response.data['results'],
            SnippetSerializer([first_snippet, second_snippet], many=True, context={'request': response.wsgi_request}).data,
        )

        response = self.client.get(reverse('snippet-list'), data={'ordering': '-created'})
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)
        self.assertEqual(
            response.data['results'],
            SnippetSerializer([second_snippet, first_snippet], many=True, context={'request': response.wsgi_request}).data,
        )

    def test_should_filter_by_language(self):
        owner = self.create_user()
        java_snippet = self.create_snippet(owner=owner, language='java')
        self.create_snippet(owner=owner, language='php')

        response = self.client.get(reverse('snippet-list'), data={'language': 'java'})
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'],
            SnippetSerializer([java_snippet], many=True, context={'request': response.wsgi_request}).data,
        )

    def test_should_filter_by_style(self):
        owner = self.create_user()
        self.create_snippet(owner=owner, style='emacs')
        vim_snippet = self.create_snippet(owner=owner, style='vim')

        response = self.client.get(reverse('snippet-list'), data={'style': 'vim'})
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'],
            SnippetSerializer([vim_snippet], many=True, context={'request': response.wsgi_request}).data,
        )

    def test_should_filter_by_owner(self):
        john = self.create_user(username='John')
        jade = self.create_user(username='Jade')
        self.create_snippet(owner=john)
        jade_snippet = self.create_snippet(owner=jade)

        response = self.client.get(reverse('snippet-list'), data={'owner': jade.id})
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'],
            SnippetSerializer([jade_snippet], many=True, context={'request': response.wsgi_request}).data,
        )

    def test_should_search_by_title_and_code(self):
        owner = self.create_user()
        first_snippet = self.create_snippet(owner=owner, title='first title')
        second_snippet = self.create_snippet(owner=owner, title='second title')
        third_snippet = self.create_snippet(owner=owner, code='the first code piece among them all')

        response = self.client.get(reverse('snippet-list'), data={'search': 'title'})
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(
            response.data['results'],
            SnippetSerializer([first_snippet, second_snippet], many=True, context={'request': response.wsgi_request}).data,
        )

        response = self.client.get(reverse('snippet-list'), data={'search': 'first'})
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(
            response.data['results'],
            SnippetSerializer([first_snippet, third_snippet], many=True, context={'request': response.wsgi_request}).data,
        )

        response = self.client.get(reverse('snippet-list'), data={'search': 'long long'})
        self.assertEqual(response.status_code, httpstatus.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])
