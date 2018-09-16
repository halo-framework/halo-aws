from __future__ import print_function

import json

from faker import Faker
from nose.tools import eq_
from rest_framework import status
from rest_framework.test import APITestCase

fake = Faker()

import django

# from django.conf import settings
# settings.configure(default_settings=settings, DEBUG=True)
django.setup()


class TestUserDetailTestCase(APITestCase):
    """
    Tests /users detail operations.
    """

    def setUp(self):
        self.url = 'http://127.0.0.1:8000/?abc=def'

    def test_get_request_returns_a_given_string(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(json.loads(response.content), {"test": "good"})

    def test_post_request_returns_a_given_code(self):
        payload = {'first_name': 'new_first_name'}
        response = self.client.post(self.url, payload)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_put_request_updates_a_code(self):
        payload = {'first_name': 'new_first_name'}
        response = self.client.put(self.url, payload)
        eq_(response.status_code, status.HTTP_200_OK)
        # print("response " + str(response))
        # eq_(response.data, 'new_first_name')

    def test_api_request_returns_a_given_string(self):
        from halolib.apis import ApiTest
        api = ApiTest('123')
        response = api.get()
        print("google response " + str(response.content))
        eq_(response.status_code, status.HTTP_200_OK)

    def test_api_request_returns_a_fail(self):
        from halolib.exceptions import ApiError
        from halolib.apis import ApiTest
        api = ApiTest('123')
        api.url = api.url + "/lgkmlgkhm??l,mhb&&,g,hj "
        try:
            response = api.get()
        except ApiError as e:
            eq_(e.status_code, status.HTTP_404_NOT_FOUND)

    def test_send_event(self):
        from halolib.events import AbsBaseEvent
        class Event1Event(AbsBaseEvent):
            target_service = 'func1'
            key_name = 'def'
            key_val = '456'

        event = Event1Event()
        dict = {"name": "david"}
        response = event.send_event(dict)
        print("event response " + str(response))
        eq_(response, 'sent event')
