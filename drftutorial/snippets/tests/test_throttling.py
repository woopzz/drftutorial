from django.urls import reverse
from rest_framework.test import APITestCase

from .common import Common


class TestThrottling(Common, APITestCase):

    def test_should_not_allow_more_than_40_rpm_for_anon_users(self):
        request = lambda: self.client.get(reverse('snippet-list'))
        self._make_requests_and_check_response_status(request, 40, 200)
        self._make_requests_and_check_response_status(request, 1, 429)

    def test_should_not_allow_more_than_60_rpm_for_auth_users(self):
        self.client.force_login(self.create_user())
        request = lambda: self.client.get(reverse('snippet-list'))

        self._make_requests_and_check_response_status(request, 60, 200)
        self._make_requests_and_check_response_status(request, 1, 429)

    def test_should_not_allow_to_create_more_than_10_snippets_in_one_minute(self):
        self.client.force_login(self.create_user())
        request = lambda: self.client.post(reverse('snippet-list'), {'code': '"code"'})

        self._make_requests_and_check_response_status(request, 10, 201)
        self._make_requests_and_check_response_status(request, 1, 429)

    def _make_requests_and_check_response_status(self, request, count, expected_status):
        for i in range(count):
            response = request()
            self.assertEqual(
                response.status_code, expected_status,
                f'{i+1}/{count}: {response.status_code} != {expected_status}',
            )
