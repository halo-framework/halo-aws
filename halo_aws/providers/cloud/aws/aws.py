from __future__ import print_function
import json
import logging
import boto3
from botocore.exceptions import ClientError
from .exceptions import ProviderError
import settings

logger = logging.getLogger(__name__)

class AwsProvider() :

    @staticmethod
    def send_event(ctx,messageDict,service_name):
        try:
            client = boto3.client('lambda', region_name=settings.AWS_REGION)
            ret = client.invoke(
                FunctionName=service_name,
                InvocationType='Event',
                LogType='None',
                Payload=bytes(json.dumps(messageDict), "utf8")
            )
            return ret
        except ClientError as e:
            #logger.error("Unexpected boto client Error", extra=dict(ctx, messageDict, e))
            raise ProviderError(e)

    @staticmethod
    def send_mail(req_context, vars, from1=None, to=None):
        from .ses import send_mail as send_mailx
        return send_mailx(req_context, vars, from1, to)

    @staticmethod
    def get_util(req_context):
        from .base_util import BaseUtil
        return BaseUtil()


