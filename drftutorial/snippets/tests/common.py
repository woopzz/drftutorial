from django.core.management import call_command

from unittest.mock import Mock

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from drftutorial.snippets.models import Snippet


class Common(TestCase):

    def setUp(self, check_throttles=False):
        self._run_on_tear_down = []

        # NOTE Really slows down the tests.
        if not check_throttles:
            _check_throttles = APIView.check_throttles
            APIView.check_throttles = Mock()
            self._run_on_tear_down.append(lambda: setattr(APIView, 'check_throttles', _check_throttles))

        super().setUp()

    def tearDown(self):
        super().tearDown()
        for func in self._run_on_tear_down:
            func()

    def create_token_and_authenticate(self, user):
        token = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')

    def create_user(self, **values):
        values.setdefault('username', 'test')
        values.setdefault('password', 'test')
        return User.objects.create_user(**values)

    def create_snippet(self, **values):
        return Snippet.objects.create(**values)

def force_rebuild_indices():
    call_command('search_index', '--rebuild', '-f')
