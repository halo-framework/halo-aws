from __future__ import print_function

# python
import logging
from abc import ABCMeta

# aws
# common
# django
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from django.template.exceptions import TemplateDoesNotExist
from rest_framework import status
from rest_framework.response import Response

from .const import HTTPChoice
from .exceptions import AuthException
from .util import Util

# Create your mixin here.

# DRF

# When a service is not responding for a certain amount of time, there should be a fallback path so users are not waiting for the response,
# but are immediately notified about the internal problem with a default response. It is the essence of a responsive design.

logger = logging.getLogger(__name__)


def get_the_template(request, name):
    return loader.get_template(name)


def get_root_url():
    if not settings.STAGE_URL:
        root = '/'
    else:
        root = "/" + settings.ENV_NAME + "/"
    return root


class AbsBaseMixin(object):
    __metaclass__ = ABCMeta

    name = 'Base'

    def __init__(self):
        self.name = self.get_name()

    def get_name(self):
        name = self.__class__.__name__
        new_name = name.replace('Link', '')
        return new_name

    def process_get(self, request, vars):
        try:
            t = get_the_template(request, self.name + '.html')
            root = get_root_url()
            c = {'the_title_string': 'welcome', 'the_site_string': settings.SITE_NAME, 'the_env_static_string': root,
                 'the_content': 'this is a get on view ' + self.name, 'version': settings.VERSION,
                 'messages': messages.get_messages(request)}
            if t:
                html = t.render(c)
            else:
                html = 'this is a get on view ' + self.name
        except TemplateDoesNotExist:
            html = 'this is a get on view ' + self.name
        return HttpResponse(html)

    def process_post(self, request, vars):
        return HttpResponse('this is a post on view ' + self.name)

    def process_put(self, request, vars):
        return HttpResponse('this is a put on view ' + self.name)

    def process_patch(self, request, vars):
        return HttpResponse('this is a patch on view ' + self.name)

    def process_delete(self, request, vars):
        return HttpResponse('this is a delete on view ' + self.name)


def check_author(request, vars, json):
    # @TODO check authorization and do masking
    return True, json, None


def check_authen(typer, request, vars):
    # @TODO check authentication and do masking
    return True, None


class AbsApiMixin(AbsBaseMixin):
    __metaclass__ = ABCMeta

    name = 'Api'
    class_name = None
    correlate_id = None
    req_context = None

    def __init__(self):
        AbsBaseMixin.__init__(self)
        self.class_name = self.__class__.__name__

    def process_in_auth(self, typer, request, vars):
        # who can use this resource with this method - api product,app,user,role,scope
        ret, cause = check_authen(typer, request, vars)
        if ret:
            ctx = Util.get_auth_context(request)
            logger.debug("ctx:" + str(ctx))
            return ctx
        raise AuthException(request, cause)

    def process_out_auth(self, request, vars, json):
        ret, jsonx, cause = check_author(request, vars, json)
        # who can use this model with this method - object,field
        if ret:
            logger.debug("jsonx:" + str(jsonx))
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
            return Response(jsonx, status=ret_status)
        return HttpResponse(status=ret_status)

    def process_post(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.post, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        json, ret_status = self.process_api(ctx, HTTPChoice.post, request, vars)
        if ret_status == status.HTTP_201_CREATED:
            jsonx = self.process_out_auth(request, vars, json)
            return Response(jsonx, status=ret_status)
        return HttpResponse(status=ret_status)

    def process_put(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.put, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        json, ret_status = self.process_api(ctx, HTTPChoice.put, request, vars)
        if ret_status == status.HTTP_202_ACCEPTED:
            jsonx = self.process_out_auth(request, vars, json)
            return Response(jsonx, status=ret_status)
        return HttpResponse(status=ret_status)

    def process_patch(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.patch, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        json, ret_status = self.process_api(ctx, HTTPChoice.patch, request, vars)
        if ret_status == status.HTTP_202_ACCEPTED:
            jsonx = self.process_out_auth(request, vars, json)
            return Response(jsonx, status=ret_status)
        return HttpResponse(status=ret_status)

    def process_delete(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.delete, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        json, ret_status = self.process_api(ctx, HTTPChoice.delete, request, vars)
        if ret_status == status.HTTP_200_OK:
            return Response(status=ret_status)
        return HttpResponse(status=ret_status)

    def process_api(self, ctx, typer, request, vars):
        return {}, 200

##################################### test #########################

from .apis import ApiTest
from .exceptions import ApiException
class TestMixin(AbsApiMixin):
    def process_api(self, ctx, typer, request, vars):
        api = ApiTest("123")
        # api.set_api_url("upcid", upc)
        api.set_api_query(request)
        try:
            ret = api.fwd_process(typer, request, vars, self.req_context)
            print("ret=" + str(ret.content))
        except ApiException as e:
            print("error=" + str(e))
        # except NoReturnApiException as e:
        #    print("NoReturnApiException="+e.message)
        return {"test": "good"}, 200


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
