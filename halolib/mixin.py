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




headers = {
    'User-Agent': 'Mozilla/5.0',
}

logger = logging.getLogger(__name__)


class BaseMixin(object):

	name = 'Base'

	def __init__(self):
		self.name = self.get_name()

	def get_name(self):
		name = self.__class__.__name__
		new_name = name.replace('Link', '')
		return new_name

	def get_root_url(self):
		if settings.SERVER_LOCAL == True or settings.STAGE_URL == False:
			root = ''
		else:
			root = "/" + settings.ENV_NAME + "/"
		return root

	def process_get(self, request, vars):
		try:
			t = self.get_the_template(request, self.name + '.html')
			root = self.get_root_url()
			c = {'the_title_string': 'welcome', 'the_site_string': settings.SITE_NAME, 'the_env_static_string': root,
				 'the_content': 'this is a get on view '+self.name, 'version': settings.VERSION,
				 'messages': messages.get_messages(request)}
			html = t.render(c)
		except TemplateDoesNotExist:
			html = 'this is a get on view ' + self.name
		return HttpResponse(html)

	def process_post(self, request, vars):
		return HttpResponse('this is a post on view ' + self.name)

	def process_put(self, request, vars):
		return HttpResponse('this is a put on view ' + self.name)

	def process_delete(self, request, vars):
		return HttpResponse('this is a delete on view ' + self.name)



##################################### test #########################

class TestMixin(BaseMixin):
	pass

