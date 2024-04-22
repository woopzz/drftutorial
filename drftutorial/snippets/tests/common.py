from django.test import TestCase
from django.contrib.auth.models import User


class Common(TestCase):

    def create_user(self, **values):
        values.setdefault('username', 'test')
        values.setdefault('password', 'test')
        return User.objects.create_user(**values)
