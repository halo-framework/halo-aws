from __future__ import print_function

# python
import datetime
import logging
from abc import ABCMeta

import requests
# aws
# common
# flask
from flask import Response as HttpResponse
from flask_api import status

from .utilx import Util
from ..const import HTTPChoice
from ..exceptions import AuthException
from ..settingsx import settingsx

settings = settingsx()

# Create your mixin here.

# DRF

# When a service is not responding for a certain amount of time, there should be a fallback path so users are not waiting for the response,
# but are immediately notified about the internal problem with a default response. It is the essence of a responsive design.

logger = logging.getLogger(__name__)

dbaccess = None


class AbsBaseMixinX(object):
    __metaclass__ = ABCMeta

    name = 'Base'

    def __init__(self):
        self.name = self.get_name()

    # def get_the_template(self, request, name):
    #    return loader.get_template(name)

    def get_root_url(self):
        """

        :return:
        """
        if not settings.STAGE_URL:
            root = '/'
        else:
            root = "/" + settings.ENV_NAME + "/"
        return root

    def get_name(self):
        """

        :return:
        """
        name = self.__class__.__name__
        new_name = name.replace('Link', '')
        return new_name

    def process_get(self, request, vars):
        """

        :param request:
        :param vars:
        :return:
        """
        html = 'this is a get on view ' + self.name
        return HttpResponse(html)

    def process_post(self, request, vars):
        """

        :param request:
        :param vars:
        :return:
        """
        return HttpResponse('this is a post on view ' + self.name)

    def process_put(self, request, vars):
        """

        :param request:
        :param vars:
        :return:
        """
        return HttpResponse('this is a put on view ' + self.name)

    def process_patch(self, request, vars):
        """

        :param request:
        :param vars:
        :return:
        """
        return HttpResponse('this is a patch on view ' + self.name)

    def process_delete(self, request, vars):
        """

        :param request:
        :param vars:
        :return:
        """
        return HttpResponse('this is a delete on view ' + self.name)

    def check_author(self, request, vars, json):
        """

        :param request:
        :param vars:
        :param json:
        :return:
        """
        # @TODO check authorization and do masking
        return True, json, None

    def check_authen(self, typer, request, vars):
        """

        :param typer:
        :param request:
        :param vars:
        :return:
        """
        # @TODO check authentication and do masking
        return True, None


class PerfMixinX(AbsBaseMixinX):
    now = None

    def process_get(self, request, vars):
        logger.debug('perf: ' + str(settings.SSM_APP_CONFIG.cache.items))
        self.now = datetime.datetime.now()
        db = request.args.get('db', None)
        urls = {}
        for item in settings.SSM_APP_CONFIG.cache.items:
            logger.debug("item=" + str(item))
            if item not in [settings.FUNC_NAME, 'DEFAULT']:
                rec = settings.SSM_APP_CONFIG.get_param(item)
                if "url" in rec:
                    url = rec["url"]
                else:
                    logger.error("service " + item + " in API_CONFIG is set to None in cache/store")
                    continue
                logger.debug("got url for " + item + ":" + url)
                if settings.FRONT_WEB is True:
                    if db is not None:
                        s = '?db=' + db
                    else:
                        s = ''
                    ret = requests.get(url + "/perf" + s)
                    urls[item] = {"url": url, "ret": str(ret.content)}
                else:
                    urls[item] = {"url": url, "ret": ''}
                for key in settings.API_CONFIG:
                    current = settings.API_CONFIG[key]
                    new_url = current["url"]
                    if "service://" + item in new_url:
                        settings.API_CONFIG[key]["url"] = new_url.replace("service://" + item, url)
        logger.debug(str(settings.API_CONFIG))
        ret = ''
        if db is not None:
            ret = self.process_db(request, vars)
        total = datetime.datetime.now() - self.now
        return HttpResponse('performance page: timing for process: ' + str(total) + " " + str(
            urls) + " " + ret + " " + settings.VERSION)

    def process_db(self, request, vars):
        logger.debug('db perf: ')
        total = datetime.datetime.now() - self.now
        return 'db access: ' + str(total)


class AbsApiMixinX(AbsBaseMixinX):
    __metaclass__ = ABCMeta

    name = 'Api'
    class_name = None
    correlate_id = None
    req_context = None

    def __init__(self):
        AbsBaseMixinX.__init__(self)
        self.class_name = self.__class__.__name__

    def process_in_auth(self, typer, request, vars):
        # who can use this resource with this method - api product,app,user,role,scope
        ret, cause = self.check_authen(typer, request, vars)
        if ret:
            ctx = Util.get_auth_context(request)
            logger.debug("ctx:" + str(ctx), extra=log_json(self.req_context))
            return ctx
        raise AuthException(request, cause)

    def process_out_auth(self, request, vars, json):
        ret, jsonx, cause = self.check_author(request, vars, json)
        # who can use this model with this method - object,field
        if ret:
            logger.debug("jsonx:" + str(jsonx), extra=log_json(self.req_context))
            return jsonx
        raise AuthException(request, cause)

    # raise AuthException(typer,resource,cause)

    def process_get(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.get, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        json, ret_status = self.process_api(ctx, HTTPChoice.get, request, vars)
        if ret_status == status.HTTP_200_OK:
            jsonx = self.process_out_auth(request, vars, json)
            return Util.json_data_response(jsonx, ret_status)  # HttpResponse(jsonx, status=ret_status)
        return HttpResponse(status=ret_status)

    def process_post(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.post, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        json, ret_status = self.process_api(ctx, HTTPChoice.post, request, vars)
        if ret_status == status.HTTP_201_CREATED:
            jsonx = self.process_out_auth(request, vars, json)
            return Util.json_data_response(jsonx, ret_status)  #HttpResponse(jsonx, status=ret_status)
        return HttpResponse(status=ret_status)

    def process_put(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.put, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        json, ret_status = self.process_api(ctx, HTTPChoice.put, request, vars)
        if ret_status == status.HTTP_202_ACCEPTED:
            jsonx = self.process_out_auth(request, vars, json)
            return Util.json_data_response(jsonx, ret_status)  #HttpResponse(jsonx, status=ret_status)
        return HttpResponse(status=ret_status)

    def process_patch(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.patch, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        json, ret_status = self.process_api(ctx, HTTPChoice.patch, request, vars)
        if ret_status == status.HTTP_202_ACCEPTED:
            jsonx = self.process_out_auth(request, vars, json)
            return Util.json_data_response(jsonx, ret_status)  #HttpResponse(jsonx, status=ret_status)
        return HttpResponse(status=ret_status)

    def process_delete(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.delete, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        json, ret_status = self.process_api(ctx, HTTPChoice.delete, request, vars)
        if ret_status == status.HTTP_200_OK:
            return Util.json_data_response(json, ret_status)  #HttpResponse(status=ret_status)
        return HttpResponse(status=ret_status)

    def process_api(self, ctx, typer, request, vars):
        return {}, 200


##################################### test #########################
import json
from ..logs import log_json
from ..apis import ApiTest
from ..exceptions import ApiError
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
                return {"test1": "bad"}, 400
            # except NoReturnApiException as e:
            #    print("NoReturnApiException="+e.message)
            # log_json(self.req_context, LogLevels.DEBUG._name_, "we did it", Util.get_req_params(request))
            return {"test2": "good"}, 200

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
                return {"test": "good"}, 200
            except SagaRollBack as e:
                return {"test": "bad"}, 500
        if typer == typer.delete:
            raise Exception("test error msg")

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


"""
class JSMixin(AbsApiMixin):
    def process_api(self, ctx, typer, request, vars):
        api = ApiLambda()
        try:
            event = get_event(request)
            func_name = "nodejs"
            swagger = get_code(api_key_id)
            code = get_code(swagger,method_id)
            event.append(code)
            ret = api.call_lambda(func_name, event)
            print str(ret.content)
        except HaloException, e:
            print str(e.message)
        return {}, 200
"""
