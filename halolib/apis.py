# Create your mixin here.

# python
import logging
from abc import ABCMeta

import requests
# aws
# common
# django
from django.conf import settings

from .exceptions import HaloError, HaloException, MaxTryHttpException

# DRF


headers = {
    'User-Agent': settings.USER_HEADERS,
}

logger = logging.getLogger(__name__)

class ApiException(HaloException):
    pass

class ApiError(HaloError):
    pass


class AbsBaseApi(object):
    __metaclass__ = ABCMeta

    name = None
    url = None

    def __init__(self):
        self.url = self.get_url_str()

    def get_url_str(self):
        api_config = settings.API_CONFIG
        logger.debug("api_config: " + str(api_config))
        return api_config[self.name]

    def set_api_url(self, key, val):
        strx = self.url
        strx = strx.replace("$" + str(key), str(val))
        logger.debug("url replace var: " + strx)
        self.url = strx
        return self.url

    def set_api_query(self, request):
        strx = self.url
        query = request.META['QUERY_STRING']
        if "?" in self.url:
            strx = strx + "&" + query
        else:
            strx = strx + "?" + query
        logger.debug("url add query: " + strx)
        self.url = strx
        return self.url

    def set_api_params(self, params):
        strx = self.url
        if "?" in self.url:
            strx = strx + "&" + params
        else:
            strx = strx + "?" + params
        logger.debug("url add query: " + strx)
        self.url = strx
        return self.url

    def exec_client(self, method, url, data=None, headers=None):
        for i in range(0, settings.HTTP_MAX_RETRY):
            try:
                return requests.request(method, url, data=data, headers=headers, timeout=settings.SERVICE_TIMEOUT_IN_MS)
            except Exception, e:
                logger.debug("method=" + method + " " + str(e.message))
                continue
        raise MaxTryHttpException(e.message)

    def process(self, method, url, data=None, headers=None):
        try:
            logger.debug("method: " + str(method) + " url: " + str(url))
            ret = self.exec_client(method, url, data=data, headers=headers)
            logger.debug("ret: " + str(ret))
            return ret
        except requests.ConnectionError, e:
            logger.debug("error: " + str(e.message))
            ret = ApiError(e.message)
            ret.status_code = -1
            raise ret
        except requests.HTTPError, e:
            logger.debug("error: " + str(e.message))
            ret = ApiError(e.message)
            ret.status_code = -2
            raise ret
        except requests.Timeout, e:
            logger.debug("error: " + str(e.message))
            ret = ApiError(e.message)
            ret.status_code = -3
            raise ret
        except requests.RequestException, e:
            logger.debug("error: " + str(e.message))
            ret = ApiError(e.message)
            ret.status_code = -4
            raise ret

    def get(self, headers=headers):
        return self.process('GET', self.url, headers=headers)

    def post(self, data, headers=headers):
        return self.process('POST', self.url, data=data, headers=headers)

    def put(self, data, headers=headers):
        return self.process('PUT', self.url, data=data, headers=headers)

    def patch(self, data, headers=headers):
        return self.process('PATCH', self.url, data=data, headers=headers)

    def delete(self, headers=headers):
        return self.process('DELETE', self.url, headers=headers)

    def fwd_process(self, typer, request, vars, headers):
        verb = typer.value
        if verb == 'GET' or 'DELETE':
            data = None
        else:
            data = request.data
        return self.process(verb, self.url, data=data, headers=headers)


##################################### lambda #########################
import boto3
import json

"""
response = client.invoke(
    FunctionName='string',
    InvocationType='Event'|'RequestResponse'|'DryRun',
    LogType='None'|'Tail',
    ClientContext='string',
    Payload=b'bytes',
    Qualifier='string'
)
"""


class ApiLambda(object):
    def call_lambda(self, func_name, event):
        client = boto3.client('lambda', region_name=settings.AWS_REGION)
        ret = client.invoke(
            FunctionName=func_name,
            InvocationType='RequestResponse',
            LogType='None',
            Payload=bytes(json.dumps(event))
        )
        return ret


##################################### test #########################


class ApiTest(AbsBaseApi):
    name = 'Google'
