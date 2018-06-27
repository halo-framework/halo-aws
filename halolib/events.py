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

class BaseEvent(object):

	def send_event(self,targetService,messageDict):
		client = boto3.client('lambda', region_name=settings.AWS_REGION)
		ret = client.invoke(
			FunctionName=targetService + +str('-') + settings.ENV_NAME,
			InvocationType='Event',
			LogType='None',
			Payload=bytes(json.dumps(messageDict))
		)

		logger.debug("send_event to service "+targetService+" ret: " + str(ret))

class BaseHandler(object):
	__metaclass__ = ABCMeta

	def get_event(self, event, context):
		logger.debug('get_event : ' + str(event))
		self.process_event(event, context)

	@abstractmethod
	def process_event(self, event, context):
		pass