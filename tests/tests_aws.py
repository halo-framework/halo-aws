from __future__ import print_function

import json
import os

from faker import Faker
from nose.tools import eq_

from halo_aws.providers.cloud.aws.aws import *
from halo_aws.providers.cloud.aws.models import AbsModel

import unittest



fake = Faker()

class TestUserDetailTestCase(unittest.TestCase):
    """
    Tests /users detail operations.
    """

    def setUp(self):
        #self.app = app#.test_client()
        self.aws = AwsProvider()


    def test_send_event(self):
        ret = self.aws.send_event({},{"msg":"tst"},"test")
        eq_(ret, {'data': {'test2': 'good'}})

    def test_send_mail(self):
        ret = self.aws.send_mail({},{"name1":"name1","email1":"email1","message1":"message1","contact1":"contact1"},"test")
        print(str(ret))
        eq_(ret, True)


    def test_get_request_returns_a_given_string2(self):
        ret = self.aws.get_util({})
        eq_(ret.get_func_name(), "FUNC_NAME")



    def test_model_get_pre(self):
        from pynamodb.attributes import UTCDateTimeAttribute, UnicodeAttribute
        class TestModel(AbsModel):
            class Meta:
                table_name = 'tbl-upc-53-loc'
                host = "http://localhost:8600"

            created_on = UTCDateTimeAttribute(null=False)
            pkey = UnicodeAttribute(hash_key=True)

        m = TestModel()
        a, b = m.get_pre()
        eq_(a, "pkey")

    def test_model_get_pre_val(self):
        from pynamodb.attributes import UTCDateTimeAttribute, UnicodeAttribute
        class TestModel(AbsModel):
            class Meta:
                table_name = 'tbl-upc-53-loc'
                host = "http://localhost:8600"

            created_on = UTCDateTimeAttribute(null=False)
            pkey = UnicodeAttribute(hash_key=True)

        m = TestModel()
        m.pkey = "123"
        a, b = m.get_pre_val()
        eq_(a, "123")

    def test_model_idem_id(self):
        from pynamodb.attributes import UTCDateTimeAttribute, UnicodeAttribute
        class TestModel(AbsModel):
            class Meta:
                table_name = 'tbl-upc-53-loc'
                host = "http://localhost:8600"

            created_on = UTCDateTimeAttribute(null=False)
            pkey = UnicodeAttribute(hash_key=True)

        m = TestModel()
        m.pkey = "456"
        ret = m.get_idempotent_id("123")
        eq_(ret, "8b077e79d995ac82ea9217c7b34c8b57")

    def test_model_idem_db(self):
        from pynamodb.attributes import UTCDateTimeAttribute, UnicodeAttribute
        from pynamodb.exceptions import PutError
        import datetime
        import uuid
        class TestModel(AbsModel):
            class Meta:
                table_name = 'tbl-upc-53-tst'
                host = "http://localhost:8600"

            created_on = UTCDateTimeAttribute(null=False)
            pkey = UnicodeAttribute(hash_key=True)

        if not TestModel.exists():
            TestModel.create_table(read_capacity_units=1, write_capacity_units=1)
        m = TestModel()
        m.pkey = str(uuid.uuid4())
        m.created_on = datetime.datetime.utcnow()
        request_id = str(uuid.uuid4())
        ret = m.save(request_id)
        try:
            ret1 = m.save(request_id)
        except PutError as e:
            print(str(e))
            ret1 = ret
        eq_(ret, ret1)


    def test_send_event1(self):
        class Event1Event():
            target_service = 'func1'
            key_name = 'def'
            key_val = '456'

        event = Event1Event()
        dict = {"name": "david"}
        try:
            response = self.aws.send_event({},dict,"tst")
            print("event response " + str(response))
            eq_(response, 'sent event')
        except Exception as e:
            print(str(e))
            eq_(e.__class__.__name__,"ProviderError")