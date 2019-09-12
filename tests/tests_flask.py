from __future__ import print_function

import json
import os

from faker import Faker
#from nose.tools import eq_

from halo_aws.providers.cloud.aws.aws import *
import unittest



fake = Faker()

class TestUserDetailTestCase(unittest.TestCase):
    """
    Tests /users detail operations.
    """

    def setUp(self):
        #self.app = app#.test_client()
        self.aws = AwsProvider()

    def test_get_request_returns_a_given_string(self):
        payload = {}
        print("response=" + str(payload))
        #eq_(payload, {'data': {'test2': 'good'}})

    def test_get_request_returns_a_given_string(self):
        self.aws.send_event({},{"msg":"tst"},"test")


    def test_get_request_returns_a_given_string1(self):
        self.aws.send_mail({},{"msg":"tst"},"test")


    def test_get_request_returns_a_given_string2(self):
        self.aws.get_util()






