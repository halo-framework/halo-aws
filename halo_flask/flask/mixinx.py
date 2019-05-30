from __future__ import print_function

# python
import datetime
import logging
from abc import ABCMeta
import json
import requests
# aws
# common
# flask
from flask import Response as HttpResponse

from .utilx import Util, status
from ..const import HTTPChoice
from ..exceptions import AuthException
from ..response import HaloResponse
from ..settingsx import settingsx
from ..logs import log_json
from ..classes import AbsBaseClass

settings = settingsx()

# Create your mixin here.

# DRF

# When a service is not responding for a certain amount of time, there should be a fallback path so users are not waiting for the response,
# but are immediately notified about the internal problem with a default response. It is the essence of a responsive design.

logger = logging.getLogger(__name__)

dbaccess = None


class AbsBaseMixinX(AbsBaseClass):
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
        ret = HaloResponse()
        ret.payload = 'this is process get on '  # + self.get_view_name()
        ret.code = 200
        ret.headers = []
        return ret

    def process_post(self, request, vars):
        """

        :param request:
        :param vars:
        :return:
        """
        ret = HaloResponse()
        ret.payload = 'this is process post on '  # + self.get_view_name()
        ret.code = 201
        ret.headers = []
        return ret

    def process_put(self, request, vars):
        """

        :param request:
        :param vars:
        :return:
        """
        ret = HaloResponse()
        ret.payload = 'this is process put on '  # + self.get_view_name()
        ret.code = 200
        ret.headers = []
        return ret

    def process_patch(self, request, vars):
        """

        :param request:
        :param vars:
        :return:
        """
        ret = HaloResponse()
        ret.payload = 'this is process patch on '  # + self.get_view_name()
        ret.code = 200
        ret.headers = []
        return ret

    def process_delete(self, request, vars):
        """

        :param request:
        :param vars:
        :return:
        """
        ret = HaloResponse()
        ret.payload = 'this is process delete on '  # + self.get_view_name()
        ret.code = 200
        ret.headers = []
        return ret

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
        # return HttpResponse('performance page: timing for process: ' + str(total) + " " + str(urls) + " " + ret + " " + settings.VERSION)
        return HaloResponse({"msg": 'performance page: timing for process: ' + str(total) + " " + str(
            urls) + " " + ret + " " + settings.VERSION}, 200, [])


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
        ret = self.process_api(ctx, HTTPChoice.get, request, vars)
        if ret.code == status.HTTP_200_OK:
            jsonx = self.process_out_auth(request, vars, ret.payload)
            ret.payload = jsonx
        return ret  #Util.json_data_response(jsonx, ret.status_code)  # HttpResponse(jsonx, status=ret_status)

    def process_post(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.post, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        ret = self.process_api(ctx, HTTPChoice.post, request, vars)
        if ret.code == status.HTTP_201_CREATED:
            jsonx = self.process_out_auth(request, vars, json)
            ret.payload = jsonx
        return ret

    def process_put(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.put, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        ret = self.process_api(ctx, HTTPChoice.put, request, vars)
        if ret.code == status.HTTP_202_ACCEPTED:
            jsonx = self.process_out_auth(request, vars, json)
            ret.payload = jsonx
        return ret

    def process_patch(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.patch, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        ret = self.process_api(ctx, HTTPChoice.patch, request, vars)
        if ret.code == status.HTTP_202_ACCEPTED:
            jsonx = self.process_out_auth(request, vars, json)
            ret.payload = jsonx
        return ret

    def process_delete(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.delete, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        ret = self.process_api(ctx, HTTPChoice.delete, request, vars)
        if ret.code == status.HTTP_200_OK:
            jsonx = self.process_out_auth(request, vars, json)
            ret.payload = jsonx
        return ret

    def process_api(self, ctx, typer, request, vars):
        return {}, 200




