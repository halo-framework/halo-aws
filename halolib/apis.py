# Create your mixin here.
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

from .exceptions import HaloError


headers = {
    'User-Agent': 'Mozilla/5.0',
}

logger = logging.getLogger(__name__)

class ApiError(HaloError):
	pass

class BaseApi(object):
	url = None

	#def __init__(self,url):
	#	self.url = url

	def set_api_url(self, key,val):
		strx = self.url
		strx = strx.replace("$" + str(key), str(val))
		logger.debug("url replace var: " + strx)
		self.url = strx
		return self.url

	def process(self,method,url,data=None,headers=None):
		try:
			ret = requests.request(str(method),url,data=data,headers=headers)
			logger.debug("ret: " + str(ret))
			return ret
		except requests.ConnectionError, e:
			logger.debug("error: " + str(e.message))
			ret = ApiError(e.message)
			ret.status_code = -1
			return ret
		except requests.HTTPError,e:
			logger.debug("error: " + str(e.message))
			ret = ApiError(e.message)
			ret.status_code = -2
			return ret
		except requests.Timeout,e:
			logger.debug("error: " + str(e.message))
			ret = ApiError(e.message)
			ret.status_code = -3
			return ret
		except requests.RequestException,e:
			logger.debug("error: " + str(e.message))
			ret = ApiError(e.message)
			ret.status_code = -4
			return ret

	def get(self,headers=None):
		return self.process('GET',self.url,headers=headers)

	def post(self, data,headers=None):
		return self.process('POST', self.url,data=data,headers=headers)

	def put(self, data,headers=None):
		return self.process('PUT', self.url,data=data,headers=headers)

	def delete(self,headers=None):
		return self.process('DELETE', self.url,headers=headers)



##################################### test #########################



