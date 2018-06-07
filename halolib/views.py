# Create your views here.
import os
import sys
import traceback
import datetime
from django.conf import settings
import logging
import uuid
import locale
import jwt
import json
import requests
import hashlib
import urlparse
import boto3
import base64
import re
import urllib

from enum import Enum
from abc import ABCMeta, abstractmethod

from urllib import quote_plus
from django.http import HttpResponse,HttpResponseRedirect
from django.template import Context, loader
from django.contrib import messages
from django.template.exceptions import TemplateDoesNotExist
from django.utils import translation

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework import status

from .mixin import BaseMixin

headers = {
    'User-Agent': 'Mozilla/5.0',
}

logger = logging.getLogger(__name__)


class HTTPChoice(Enum):   # A subclass of Enum
    get = "get"
    post = "post"
    put = "put"
    delete = "delete"

def strx(str1):
    if str1:
        try:
            return str1.encode('utf-8').strip()
        except Exception,e:
            return str(str1)
        except AttributeError,e:
            return str(str1)
    return ''

class Util:

    @staticmethod
    def mobile(request):
        """Return True if the request comes from a mobile device."""

        MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)

        if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
            return True
        else:
            return False

    @staticmethod
    def get_chrome_browser(request):

        CHROME_AGENT_RE = re.compile(r".*(Chrome)", re.IGNORECASE)
        NON_CHROME_AGENT_RE = re.compile(r".*(Aviator | ChromePlus | coc_ | Dragon | Edge | Flock | Iron | Kinza | Maxthon | MxNitro | Nichrome | OPR | Perk | Rockmelt | Seznam | Sleipnir | Spark | UBrowser | Vivaldi | WebExplorer | YaBrowser)", re.IGNORECASE)


        if CHROME_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
            if NON_CHROME_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
                return False
            else:
                return True
        else:
            return False

    @staticmethod
    def check_if_robot():
        return False


class BaseLink(APIView):
    __metaclass__ = ABCMeta

    """
        View to list all users in the system.

        * Requires token authentication.
        * Only admin users are able to access this view.
        """

    # authentication_classes = (authentication.TokenAuthentication,)
    # permission_classes = (permissions.IsAdminUser,permissions.IsAuthenticatedOrReadOnly)
    permission_classes = (permissions.AllowAny,)

    the_html = ''
    the_tag = ''
    other_html = ''
    other_tag = ''

    user_languages = []
    user_locale = settings.LOCALE_CODE
    user_lang = settings.LANGUAGE_CODE

    def do_process(self, request,typer,vars):

        now = datetime.datetime.now()

        self.get_user_locale(request)
        logger.info('process LANGUAGE:  ' + str(self.user_lang)+" LOCALE: "+str(self.user_locale))

        try:
            ret = self.process(request,typer,vars)
            total = datetime.datetime.now() - now
            logger.info("timing for "+str(typer) + str(total))
            return ret
        except IOError as e:
            logger.debug('An IOerror occured :' + str(e.message))
            logger.info('An IOError occurred in ' + str(traceback.format_exc()))

        except ValueError as e:
            logger.debug('Non-numeric data found : '+ str(e.message))
            logger.info('An ValueError occurred in ' + str(traceback.format_exc()))

        except ImportError as e:
            logger.debug("NO module found")
            logger.info('An ImportError occurred in ' + str(traceback.format_exc()))

        except EOFError as e:
            logger.debug('Why did you do an EOF on me?')
            logger.info('An EOFError occurred in ' + str(traceback.format_exc()))

        except KeyboardInterrupt as e:
            logger.debug('You cancelled the operation.')
            logger.info('An KeyboardInterrupt occurred in ' + str(traceback.format_exc()))

        except Exception as e:
            #exc_type, exc_obj, exc_tb = sys.exc_info()
            #fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #logger.debug('An error occured in '+str(fname)+' lineno: '+str(exc_tb.tb_lineno)+' exc_type '+str(exc_type)+' '+e.message)
            logger.info('An Exception occurred in ' + str(traceback.format_exc()))

        else:
            self.process_else()

        finally:
            self.process_finally()

        html = '<html>error in request</html>'
        total = datetime.datetime.now() - now
        logger.info("timing for " +str(typer) + ' ' + str(total))
        return HttpResponseRedirect("/"+str(status.HTTP_400_BAD_REQUEST))

    def process_else(self):
        logger.debug("process_else")

    def process_finally(self):
        logger.debug("process_finally")

    def put_in_q(self,urlx, type, uuid ,height=None, width=None):
        logger.debug("put in q: "+str(urlx))
        #in the q
        hash = self.get_hash(urlx)
        score = self.score_item(urlx)
        self.add_url_db(hash, urlx, score, height,width, type)

    def get_hash(self,urlx):
        return hashlib.sha256(urlx.encode()).hexdigest()

    def all_locale(self,loc=None):
        alllocale = locale.locale_alias
        if loc:
            for k in alllocale.keys():
                print 'locale[%s] %s' % (k, alllocale[k])
                if alllocale[k] == loc:
                    return True
        if settings.DEBUG:
            for k in alllocale.keys():
                print 'locale[%s] %s' % (k, alllocale[k])
        return False

    def split_locale_from_request(self, request):
        locale = ''
        if request.META.get("QUERY_STRING", ""):
            path = request.META['QUERY_STRING']
            logger.debug('QUERY_STRING:  ' + str(path))
            key = "_="
            if key in path:
                if "&" in path:
                    list = path.split("&")
                    for l in list:
                        param = l
                        if key in param:
                            vals = param.split("=")
                            if len(vals) > 1:
                                locale = vals[1]
                else:
                    vals = path.split("=")
                    if len(vals) > 1:
                        locale = vals[1]
        logger.debug('split_locale_from_request:  ' + str(locale))
        return locale

    #es,ar;q=0.9,he-IL;q=0.8,he;q=0.7,en-US;q=0.6,en;q=0.5,es-ES;q=0.4
    def get_user_locale(self, request):
        locale = self.split_locale_from_request(request)
        if (not locale) or (locale == ''):
            if request.META.has_key('HTTP_ACCEPT_LANGUAGE'):
                self.user_languages = request.META.get('HTTP_ACCEPT_LANGUAGE', self.user_locale+",")
                logger.debug('user_languages:  ' + str(self.user_languages))
                arr = self.user_languages.split(",")
                for l in arr:
                   if "-" in l:
                        if ";" not in l:
                            self.user_locale = l
                        else:
                            self.user_locale = l.split(";")[0]
                        break
                   else:
                       continue
        else:
            self.user_locale = locale
        logger.debug('process LOCALE_CODE:  ' + str(self.user_locale))
        if settings.GET_LANGUAGE == True:
            #translation.activate(self.user_locale)
            self.user_lang = self.user_locale.split("-")[0]#translation.get_language().split("-")[0]
        logger.debug('process LANGUAGE_CODE:  ' + str(self.user_lang))


    def get(self, request, format=None):
        logger.debug('process')
        vars = {}
        return self.do_process(request,HTTPChoice.get,vars);

    def post(self, request, format=None):
        logger.debug('process')
        vars = {}
        return self.do_process(request,HTTPChoice.post, vars);

    def put(self, request, format=None):
        logger.debug('process')
        vars = {}
        return self.do_process(request,HTTPChoice.put, vars);

    def delete(self, request, format=None):
        logger.debug('process')
        vars = {}
        return self.do_process(request,HTTPChoice.delete, vars);

    def process(self,request,typer,vars):
        """
        Return a list of all users.
        """
        self.user_langs = request.META.get('HTTP_ACCEPT_LANGUAGE', ['en-US', ])
        logger.debug('process user_langs:  '+str(self.user_langs))

        if typer == HTTPChoice.get:
            return self.process_get(request,vars)

        if typer == HTTPChoice.post:
            return self.process_post(request,vars)

        if typer == HTTPChoice.put:
            return self.process_put(request,vars)

        if typer == HTTPChoice.delete:
            return self.process_delete(request,vars)

        return HttpResponse('this is a '+str(typer)+' on '+self.get_view_name())

    def process_get(self,request,vars):
        logger.debug("its done ")
        return HttpResponse('this is process get on '+self.get_view_name())

    def process_post(self,request,vars):
        logger.debug("its done ")
        return HttpResponse('this is process post on '+self.get_view_name())

    def process_put(self,request,vars):
        logger.debug("its done ")
        return HttpResponse('this is process put on '+self.get_view_name())

    def process_delete(self,request,vars):
        logger.debug("its done ")
        return HttpResponse('this is process delete on '+self.get_view_name())

    def get_the_template(self, request,html):
        return loader.get_template(html)

    def get_template(self, request):
        if Util.mobile(request):
            t = loader.get_template(self.the_html)
            the_mobile_web = self.the_tag
        else:
            t = loader.get_template(self.other_html)
            the_mobile_web = self.other_tag
        return t, the_mobile_web

    def get_client_ip(self,request):
        logger.debug("get_client_ip: " + str(request.META))
        ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_jwt(self, request):
        logger.debug("get_jwt: " )
        ip = self.get_client_ip(request)
        logger.debug("get_jwt ip: " + str(ip))
        encoded_token = jwt.encode({'ip': ip}, settings.SECRET_JWT_KEY, algorithm ='HS256')
        logger.debug("get_jwt: " + str(encoded_token))
        return encoded_token

    def check_jwt(self, request):#return true if token matches
        ip = self.get_client_ip(request)
        encoded_token = request.GET.get('jwt',None)
        logger.debug("check_jwt: " + str(encoded_token))
        if not encoded_token:
            return False
        decoded_token = jwt.decode(encoded_token, settings.SECRET_JWT_KEY, algorithm ='HS256')
        logger.debug("check_jwt decoded_token: " + str(decoded_token)+ ' ip '+str(ip))
        return ip == decoded_token['ip']

    def get_jwt_str(self, request):
        logger.debug("get_jwt_str: ")
        return '&jwt='+self.get_jwt(request)



##################################### test #########################

class TestLink(BaseMixin,BaseLink):
    permission_classes = (permissions.AllowAny,)

