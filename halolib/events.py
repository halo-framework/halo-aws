# Create your mixin here.

# python
import json
import logging
from abc import ABCMeta, abstractmethod

# aws
import boto3
# common
# django
from django.conf import settings

# DRF

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