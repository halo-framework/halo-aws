# Create your mixin here.

# python
import logging
from abc import ABCMeta, abstractmethod

# aws
# common
# django
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from django.template.exceptions import TemplateDoesNotExist

from .const import HTTPChoice
from .exceptions import AuthException
from .util import Util

# DRF

# When a service is not responding for a certain amount of time, there should be a fallback path so users are not waiting for the response,
# but are immediately notified about the internal problem with a default response. It is the essence of a responsive design.

logger = logging.getLogger(__name__)


class AbsBaseMixin(object):
    __metaclass__ = ABCMeta

    name = 'Base'

    def __init__(self):
        self.name = self.get_name()

    def get_name(self):
        name = self.__class__.__name__
        new_name = name.replace('Link', '')
        return new_name

    def get_root_url(self):
        if settings.SERVER_LOCAL == True or settings.STAGE_URL == False:
            root = '/'
        else:
            root = "/" + settings.ENV_NAME + "/"
        return root

    def get_the_template(self, request, name):
        return loader.get_template(name)

    def process_get(self, request, vars):
        try:
            t = self.get_the_template(request, self.name + '.html')
            root = self.get_root_url()
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


class AbsApiMixin(AbsBaseMixin):
    __metaclass__ = ABCMeta

    name = 'Api'
    class_name = None

    def __init__(self):
        self.name = self.get_name()
        self.class_name = self.__class__.__name__

    def check_auth(self, typer, request, vars):
        # @TODO check authentication and do masking
        return True, None

    def process_in_auth(self, typer, request, vars):
        # who can use this resource with this method - api product,app,user,role,scope
        ret, cause = self.check_auth(typer, request, vars)
        if ret:
            ctx = Util.get_req_context(request)
            return ctx
        raise AuthException(typer, request, cause)

    def process_out_auth(self, request, vars, json, ret_status):
        # who can use this model with this method - object,field
        return True
        # raise AuthException(typer,resource,cause)

    def process_get(self, request, vars):
        ctx = self.process_in_auth(HTTPChoice.get, request, vars)
        json, ret_status = self.process_api(ctx, request, vars)
        self.process_out_auth(request, vars, json, ret_status)
        return HttpResponse('this is an auth get on view ' + self.name, status=ret_status)

    def process_post(self, request, vars):
        ctx = self.process_in_auth(HTTPChoice.post, request, vars)
        json, ret_status = self.process_api(ctx, request, vars)
        self.process_out_auth(request, vars, json, ret_status)
        return HttpResponse('this is an auth post on view ' + self.name, status=ret_status)

    def process_put(self, request, vars):
        ctx = self.process_in_auth(HTTPChoice.put, request, vars)
        json, ret_status = self.process_api(ctx, request, vars)
        self.process_out_auth(request, vars, json, ret_status)
        return HttpResponse('this is an auth put on view ' + self.name, status=ret_status)

    def process_patch(self, request, vars):
        ctx = self.process_in_auth(HTTPChoice.patch, request, vars)
        json, ret_status = self.process_api(ctx, request, vars)
        self.process_out_auth(request, vars, json, ret_status)
        return HttpResponse('this is an auth patch on view ' + self.name, status=ret_status)

    def process_delete(self, request, vars):
        ctx = self.process_in_auth(HTTPChoice.delete, request, vars)
        json, ret_status = self.process_api(ctx, request, vars)
        self.process_out_auth(request, vars, json, ret_status)
        return HttpResponse('this is an auth delete on view ' + self.name, status=ret_status)

    @abstractmethod
    def process_api(self, ctx, request, vars):
        pass

##################################### test #########################

class TestMixin(AbsApiMixin):
    def process_api(self, ctx, request, vars):
        headers = ctx
        return {}, 200
