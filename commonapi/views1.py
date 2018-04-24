# Create your views here.
import os
import sys
import traceback
import datetime
from django.conf import settings
import logging

from urllib import quote_plus
from django.http import HttpResponse,HttpResponseRedirect
import json
import requests
import hashlib
import urlparse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework import status

import cache
#from PIL import Image

"""
ISBN (International Standard Book Number): 10 digits or 13 digits

UPC (Universal Product Code): 12 digits

EAN (European Article Number): 13 digits

JAN (Japanese Article Number): 13 digits

GTIN-14 (Global Trade Item Number): 14 digits

ASIN (Amazon Standard Identification Number)
"""

headers = {
    'User-Agent': 'Mozilla/5.0',
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class BaseLink(APIView):

    """
        View to list all users in the system.

        * Requires token authentication.
        * Only admin users are able to access this view.
        """
    # authentication_classes = (authentication.TokenAuthentication,)
    # permission_classes = (permissions.IsAdminUser,permissions.IsAuthenticatedOrReadOnly)
    permission_classes = (permissions.AllowAny,)

    def do_process(self, request,type,name,vars):

        now = datetime.datetime.now()

        try:
            ret = self.process(request,vars)
            total = datetime.datetime.now() - now
            logger.info("timing for "+type +' '+name+' '+ str(total))
            return ret
        except IOError as e:
            logger.debug('An IOerror occured :' + e.message)
            logger.info('An IOError occured in ' + str(traceback.format_exc()))

        except ValueError as e:
            logger.debug('Non-numeric data found : '+e.message)
            logger.info('An ValueError occured in ' + str(traceback.format_exc()))

        except ImportError as e:
            logger.debug("NO module found")
            logger.info('An ImportError occured in ' + str(traceback.format_exc()))

        except EOFError as e:
            logger.debug('Why did you do an EOF on me?')
            logger.info('An EOFError occured in ' + str(traceback.format_exc()))

        except KeyboardInterrupt as e:
            logger.debug('You cancelled the operation.')
            logger.info('An KeyboardInterrupt occured in ' + str(traceback.format_exc()))

        except Exception as e:
            #exc_type, exc_obj, exc_tb = sys.exc_info()
            #fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #logger.debug('An error occured in '+str(fname)+' lineno: '+str(exc_tb.tb_lineno)+' exc_type '+str(exc_type)+' '+e.message)
            logger.info('An Exception occured in ' + str(traceback.format_exc()))

        else:
            self.process_else()

        finally:
            self.process_finally()

        html = '<html>error in request</html>'
        total = datetime.datetime.now() - now
        logger.info("timing for " + type + ' ' + name + ' ' + str(total))
        return HttpResponse(status.HTTP_400_BAD_REQUEST,html)

    def process_else(self):
        logger.debug("process_else")

    def process_finally(self):
        logger.debug("process_finally")

    def put_in_q(self,urlx, type, uuid ,height=None, width=None):
        logger.debug("put in q: "+urlx)
        #in the q
        hash = self.get_hash(urlx)
        score = self.score_item(urlx)
        self.add_url_db(hash, urlx, score, height,width, type)

    def get_hash(self,urlx):
        return hashlib.sha256(urlx.encode()).hexdigest()

    def get(self, request, format=None):
        if check_if_robot():
            html = '<html>are you a robot?</html>'
            return HttpResponse(html)
        logger.debug('process GET:  ')
        test = None
        if settings.DEV == settings.ENV_NAME:
            test = request.GET.get('test')
        vars = {}
        #return self.process(request,urlx,type,uuid,test,height,width)
        return self.do_process(request,"GET",'BaseLink',vars);

    def post(self, request, format=None):
        if check_if_robot():
            html = '<html>are you a robot?</html>'
            return HttpResponse(html)
        logger.debug('process POST:  ')
        test = None
        if settings.DEV == settings.ENV_NAME:
            test = request.POST.get('test')
        vars = {}
        #return self.process(request,urlx,type,uuid,test,height,width)
        return self.do_process(request,"POST",'BaseLink', vars);

    def process(self,request,vars):
        """
        Return a list of all users.
        """
        #can not block root sites except black list
        if self.is_root_site(request.get_IP()):
            return HttpResponse()

        return HttpResponse()



def check_if_robot():
    # TODO fix the robot
    return False

