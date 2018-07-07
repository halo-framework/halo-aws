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
from halolib.exceptions import HaloException

logger = logging.getLogger(__name__)


class NoMessageException(HaloException):
    pass

class AbsBaseEvent(object):
    __metaclass__ = ABCMeta

    target_service = None
    key_name = None
    key_val = None

    def send_event(self, messageDict):
        if messageDict:
            messageDict[self.key_name] = self.key_val
            messageDict[self.target_service + 'service_task_id'] = 'y'
        else:
            raise NoMessageException()
        client = boto3.client('lambda', region_name=settings.AWS_REGION)
        ret = client.invoke(
            FunctionName=self.target_service + str('-') + settings.ENV_NAME,
            InvocationType='Event',
            LogType='None',
            Payload=bytes(json.dumps(messageDict))
        )

        logger.debug("send_event to service " + self.target_service + " ret: " + str(ret))

        return ret


class AbsMainHandler(object):
	__metaclass__ = ABCMeta

	keys = []
	vals = {}
	classes = {}

	def get_event(self, event, context):
		logger.debug('get_event : ' + str(event))
		self.process_event(event, context)

	@abstractmethod
	def process_event(self, event, context):
		for key in self.keys:
			if key in event:
				val = self.vals[key]
				if val == event[key]:
					class_name = self.classes[key]
					module = __import__('mixin_handler')
					class_ = getattr(module, class_name)
					instance = class_()
					instance.do_event(self, event, context)


class AbsBaseHandler(object):
    __metaclass__ = ABCMeta

    key_name = None
    key_val = None

    def do_event(self, event, context):
        correlate_id = ''
        user_agent = ''
        if "x-correlation-id" in event:
            correlate_id = event["x-correlation-id"]
        if "User-Agent" in event:
            user_agent = event["User-Agent"]
        if "Debug-Log-Enabled" in event:
            debug_flag = event["Debug-Log-Enabled"]
        logprefix = "Correlate-ID: " + correlate_id + " User-Agent: " + user_agent + " -  ";
        logger.debug(logprefix + 'get_event : ' + str(event))
        self.process_event(event, context)

    @abstractmethod
    def process_event(self, event, context):
        pass
