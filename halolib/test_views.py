from django.test import Client
from faker import Faker
from nose.tools import eq_
from rest_framework import status
from rest_framework.test import APITestCase

fake = Faker()

import django

django.setup()


class TestUserDetailTestCase(APITestCase):
    """
    Tests /users detail operations.
    """

    def setUp(self):
        self.url = 'http://127.0.0.1:8000'
        # initialize the APIClient app
        self.client = Client()

    def test_get_request_returns_a_given_user(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_post_request_returns_a_given_string(self):
        response = self.client.post(self.url)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_put_request_updates_a_user(self):
        payload = {'first_name': 'new_first_name'}
        response = self.client.put(self.url, payload)
        eq_(response.status_code, status.HTTP_200_OK)
        print "response", str(response)
        # eq_(response.data, 'new_first_name')
