from __future__ import print_function

import json
import os

from faker import Faker
from flask import Flask, request
from flask_restful import Api
from nose.tools import eq_

fake = Faker()

from halo_flask.flask.utilx import Util, status
from halo_flask.exceptions import ApiError
from halo_flask.logs import log_json
from halo_flask import saga
from halo_flask.models import AbsModel
import unittest
import requests

app = Flask(__name__)
api = Api(app)
app.config.from_object('settings')


class TestUserDetailTestCase(unittest.TestCase):
    """
    Tests /users detail operations.
    """

    def setUp(self):
        self.url = 'http://127.0.0.1:8000/?abc=def'
        self.perf_url = 'http://127.0.0.1:8000/perf'

    def test_get_request_returns_a_given_string(self):
        response = requests.get(self.url)
        print("response=" + str(response.content))
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(json.loads(response.content), {'data': {'test2': 'good'}})

    def test_api_request_returns_a_given_string(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            api = ApiTest(Util.get_req_context(request))
            timeout = Util.get_timeout(request)
            try:
                response = api.get(timeout)
            except ApiError as e:
                #eq_(e.status_code, status.HTTP_403_NOT_FOUND)
                eq_(e.__class__.__name__,"CircuitBreakerError")

    def test_api_request_returns_a_given_string1(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            api = GoogleApi(Util.get_req_context(request))
            timeout = Util.get_timeout(request)
            try:
                response = api.get(timeout)
            except ApiError as e:
                #eq_(e.status_code, status.HTTP_403_NOT_FOUND)
                eq_(e.__class__.__name__,"CircuitBreakerError")

    def test_api_request_returns_a_fail(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            api = ApiTest(Util.get_req_context(request))
            api.url = api.url + "/lgkmlgkhm??l,mhb&&,g,hj "
            timeout = Util.get_timeout(request)
            try:
                response = api.get(timeout)
            except ApiError as e:
                #eq_(e.status_code, status.HTTP_403_NOT_FOUND)
                eq_(e.__class__.__name__,"CircuitBreakerError")

    def test_send_event(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            from halo_flask.events import AbsBaseEvent
            class Event1Event(AbsBaseEvent):
                target_service = 'func1'
                key_name = 'def'
                key_val = '456'

            event = Event1Event()
            dict = {"name": "david"}
            response = event.send_event(dict)
            print("event response " + str(response))
            eq_(response, 'sent event')

    def test_system_debug_enabled(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            os.environ['DEBUG_LOG'] = 'true'
            flag = 'false'
            for i in range(0, 80):
                ret = Util.get_system_debug_enabled()
                print(ret)
                if ret == 'true':
                    flag = ret
            eq_(flag, 'true')

    def test_debug_enabled(self):
        header = {'HTTP_DEBUG_LOG_ENABLED': 'true'}
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            ret = Util.get_req_context(request)
            eq_(ret["debug-log-enabled"], 'true')

    def test_json_log(self):
        import traceback
        header = {'HTTP_DEBUG_LOG_ENABLED': 'true'}
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            req_context = Util.get_req_context(request)
            try:
                raise Exception("test it")
            except Exception as e:
                e.stack = traceback.format_exc()
                ret = log_json(req_context, {"abc": "def"}, err=e)
                print(str(ret))
                eq_(ret["debug-log-enabled"], 'true')

    def test_get_request_with_debug(self):
        header = {'HTTP_DEBUG_LOG_ENABLED': 'true'}
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            ret = Util.get_debug_enabled(request)
            eq_(ret, 'true')

    def test_debug_event(self):
        event = {'debug-log-enabled': 'true'}
        ret = Util.get_correlation_from_event(event)
        eq_(Util.event_req_context["debug-log-enabled"], 'true')
        ret = Util.get_correlation_from_event(event)
        eq_(ret["debug-log-enabled"], 'true')

    def test_pref_mixin(self):
        response = requests.get(self.perf_url)
        eq_(response.status_code, status.HTTP_200_OK)

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

    def test_load_saga(self):
        with open("saga.json") as f:
            jsonx = json.load(f)
        with open("schema.json") as f1:
            schema = json.load(f1)
        sagax = saga.load_saga("test", jsonx, schema)
        eq_(len(sagax.actions), 6)

    def test_run_saga(self):
        response = requests.put(self.url)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_rollback_saga(self):
        response = requests.post(self.url)
        eq_(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_ssm(self):  # @TODO
        from halo_flask.ssm import get_app_config
        ret = get_app_config("us-east-1")
        eq_(ret.get_param("halo_flask")["url"], 'https://127.0.0.1:8000/loc')

    def test_error_handler(self):
        response = requests.delete(self.url)
        #print("x="+str(response.content))
        #print("ret=" + str(json.loads(response.content)))
        #eq_(json.loads(response.content)['error']['error_message'], 'test error msg')
        eq_(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_timeout(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "halo_flask"
            timeout = Util.get_timeout(request)
            eq_(timeout, 3)



##################################### test #########################
from halo_flask.apis import AbsBaseApi

class ApiTest(AbsBaseApi):
    name = 'Cnn'


class GoogleApi(AbsBaseApi):
    name = 'Google'


API_LIST = {"Google": 'GoogleApi', "Cnn": "ApiTest"}


##################################### test #########################
import json
from ..logs import log_json
from ..apis import ApiTest
from ..exceptions import ApiError, ApiException
from ..saga import load_saga, SagaRollBack


class TestMixinX(AbsApiMixinX):
    def process_api(self, ctx, typer, request, vars):
        self.upc = "123"
        self.typer = typer
        if typer == typer.get:
            logger.debug("start get")
            api = ApiTest(self.req_context)
            # api.set_api_url("upcid", upc)
            # api.set_api_query(request)
            timeout = Util.get_timeout(request)
            try:
                ret = api.get(timeout)
            except ApiError as e:
                logger.debug("we did it", extra=log_json(self.req_context, Util.get_req_params(request), e))
                ret = HaloResponse()
                ret.payload = {"test1": "bad"}
                ret.code = 400
                ret.headers = []
                return ret
            # except NoReturnApiException as e:
            #    print("NoReturnApiException="+e.message)
            # log_json(self.req_context, LogLevels.DEBUG._name_, "we did it", Util.get_req_params(request))
            ret = HaloResponse()
            ret.payload = {"test2": "good"}
            ret.code = 200
            ret.headers = []
            return ret

        if typer == typer.post or typer == typer.put:
            logger.debug("start " + str(typer))
            with open("C:\\dev\\projects\\halo\halo_lib\\saga.json") as f:
                jsonx = json.load(f)
            with open("C:\\dev\\projects\\halo\halo_lib\\schema.json") as f1:
                schema = json.load(f1)
            sagax = load_saga("test", jsonx, schema)
            payloads = {"BookHotel": {"abc": "def"}, "BookFlight": {"abc": "def"}, "BookRental": {"abc": "def"},
                        "CancelHotel": {"abc": "def"}, "CancelFlight": {"abc": "def"}, "CancelRental": {"abc": "def"}}
            apis = {"BookHotel": self.create_api1, "BookFlight": self.create_api2, "BookRental": self.create_api3,
                    "CancelHotel": self.create_api4, "CancelFlight": self.create_api5, "CancelRental": self.create_api6}
            try:
                self.context = Util.get_lambda_context(request)
                ret = sagax.execute(self.req_context, payloads, apis)
                ret = HaloResponse()
                ret.payload = {"test": "good"}
                ret.code = 200
                ret.headers = []
                return ret
            except SagaRollBack as e:
                ret = HaloResponse()
                ret.payload = {"test": "bad"}
                ret.code = 500
                ret.headers = []
                return ret
        if typer == typer.delete:
            raise ApiException("test error msg")

    def create_api1(self, api, results, payload):
        print("create_api1=" + str(api) + " result=" + str(results))
        api.set_api_url("upcid", self.upc)
        if self.context:
            timeout = Util.get_timeout_milli(self.context)
        else:
            timeout = 100
        return api.get(timeout)

    def create_api2(self, api, results, payload):
        print("create_api2=" + str(api) + " result=" + str(results))
        api.set_api_url("upcid", self.upc)
        if self.context:
            timeout = Util.get_timeout_milli(self.context)
        else:
            timeout = 100
        return api.get(timeout)

    def create_api3(self, api, results, payload):
        print("create_api3=" + str(api) + " result=" + str(results))
        api.set_api_url("upcid", self.upc)
        if self.context:
            timeout = Util.get_timeout_milli(self.context)
        else:
            timeout = 100
        if self.typer == self.typer.post:
            return api.post(payload, timeout)
        return api.get(timeout)

    def create_api4(self, api, results, payload):
        print("create_api4=" + str(api) + " result=" + str(results))
        api.set_api_url("upcid", self.upc)
        if self.context:
            timeout = Util.get_timeout_milli(self.context)
        else:
            timeout = 100
        return api.get(timeout)

    def create_api5(self, api, results, payload):
        print("create_api5=" + str(api) + " result=" + str(results))
        api.set_api_url("upcid", self.upc)
        if self.context:
            timeout = Util.get_timeout_milli(self.context)
        else:
            timeout = 100
        return api.get(timeout)

    def create_api6(self, api, results, payload):
        print("create_api6=" + str(api) + " result=" + str(results))
        api.set_api_url("upcid", self.upc)
        if self.context:
            timeout = Util.get_timeout_milli(self.context)
        else:
            timeout = 100
        return api.get(timeout)