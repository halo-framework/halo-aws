from __future__ import print_function

import importlib
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
from halolib.util import Util

logger = logging.getLogger(__name__)


class NoMessageException(HaloException):
    pass


class NoTargetUrlException(HaloException):
    pass

class AbsBaseEvent(object):
    __metaclass__ = ABCMeta

    target_service = None
    key_name = None
    key_val = None

    def get_loc_url(self):
        if self.target_service in settings.LOC_TABLE:
            return settings.LOC_TABLE[self.target_service]
        raise NoTargetUrlException()

    def send_event(self, messageDict, request=None, ctx=None):
        if messageDict:
            messageDict[self.key_name] = self.key_val
            messageDict[self.target_service + 'service_task_id'] = 'y'
            if request:
                ctx = Util.get_req_context(request)
            if ctx:
                messageDict.update(ctx)
        else:
            raise NoMessageException()
        if settings.SERVER_LOCAL == True:
            from multiprocessing.dummy import Pool
            import requests
            url = self.get_loc_url()
            pool = Pool(1)
            futures = []
            for x in range(1):
                futures.append(pool.apply_async(requests.post, [url], {'data': messageDict}))
            for future in futures:
                logger.debug("future:" + str(future.get()))
            return "sent event"
        else:
            client = boto3.client('lambda', region_name=settings.AWS_REGION)
            ret = client.invoke(
                    FunctionName=self.target_service + str('-') + settings.ENV_NAME.replace("_", "-"),
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

    def process_event(self, event, context):
        for key in self.keys:
            if key in event:
                val = self.vals[key]
                if val == event[key]:
                    class_name = self.classes[key]
                    module = importlib.import_module(settings.MIXIN_HANDLER)
                    logger.debug('module : ' + str(module))
                    class_ = getattr(module, class_name)
                    instance = class_()
                    instance.do_event(event, context)


class AbsBaseHandler(object):
    __metaclass__ = ABCMeta

    key_name = None
    key_val = None

    def do_event(self, event, context):
        logprefix = Util.get_correlation_from_event(event)
        logger.debug(logprefix + ' get_event : ' + str(event))
        self.process_event(event, context)

    @abstractmethod
    def process_event(self, event, context):
        pass
