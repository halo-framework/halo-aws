# Create your mixin here.
# python
import datetime
import json
import logging
import urllib
import uuid
import requests
from cStringIO import StringIO
# aws
import boto3
from botocore.exceptions import ClientError
# common
from halolib.views import HTTPChoice
from halolib.apis import BaseApi
# django
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
# DRF
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from enum import Enum
from abc import ABCMeta, abstractmethod

from .exceptions import HaloError,HaloException

headers = {
    'User-Agent': settings.headers,
}

logger = logging.getLogger(__name__)

class BaseEvent(object):
	__metaclass__ = ABCMeta

	target_service = None

	def send_event(self,messageDict):
		client = boto3.client('lambda', region_name=settings.AWS_REGION)
		ret = client.invoke(
			FunctionName=self.target_service+str('-') + settings.ENV_NAME,
			InvocationType='Event',
			LogType='None',
			Payload=bytes(json.dumps(messageDict))
		)

		logger.debug("send_event to service "+self.target_service+" ret: " + str(ret))

class BaseHandler(object):
	__metaclass__ = ABCMeta

	def get_event(self, event, context):
		logger.debug('get_event : ' + str(event))
		self.process_event(event, context)

	@abstractmethod
	def process_event(self, event, context):
		pass