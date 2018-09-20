from __future__ import print_function

# python
import datetime
import logging
import time
from abc import ABCMeta

import requests
# aws
# common
# django
from django.conf import settings

from .exceptions import MaxTryHttpException, ApiError
from .logs import log_json

# DRF


headers = {
    'User-Agent': settings.USER_HEADERS,
}

logger = logging.getLogger(__name__)


def exec_client(req_context, method, url, api_type, data=None, headers=None):
    msg = "Max Try"
    for i in range(0, settings.HTTP_MAX_RETRY):
        try:
            logger.debug(log_json(req_context, logging.DEBUG, "try: " + str(i)))
            ret = requests.request(method, url, data=data, headers=headers,
                                   timeout=(
                                   settings.SERVICE_CONNECT_TIMEOUT_IN_MS, settings.SERVICE_READ_TIMEOUT_IN_MS))
            logger.debug(log_json(req_context, logging.DEBUG, "status_code=" + str(ret.status_code)))
            if ret.status_code >= 500:
                if i > 0:
                    time.sleep(settings.HTTP_RETRY_SLEEP)
                continue
            if 200 > ret.status_code or 500 > ret.status_code >= 300:
                err = ApiError("error status_code " + str(ret.status_code) + " in : " + url)
                err.status_code = ret.status_code
                err.stack = None
                raise err
            return ret
        except requests.exceptions.ReadTimeout:  # this confirms you that the request has reached server
            logger.debug(log_json(req_context, logging.DEBUG, "ReadTimeout " + str(
                settings.SERVICE_READ_TIMEOUT_IN_MS) + " in method=" + method + " for url=" + url))
            "status_code=" + str(ret.status_code)
            if i > 0:
                time.sleep(settings.HTTP_RETRY_SLEEP)
            continue
        except requests.exceptions.ConnectTimeout:
            logger.debug(log_json(req_context, logging.DEBUG, "ConnectTimeout in method=" + str(
                settings.SERVICE_CONNECT_TIMEOUT_IN_MS) + " in method=" + method + " for url=" + url))
            if i > 0:
                time.sleep(settings.HTTP_RETRY_SLEEP)
            continue
    raise MaxTryHttpException(msg)


class AbsBaseApi(object):
    __metaclass__ = ABCMeta

    name = None
    url = None
    api_type = None
    req_context = None

    def __init__(self, req_context):
        self.req_context = req_context
        self.url, self.api_type = self.get_url_str()

    def get_url_str(self):
        api_config = settings.API_CONFIG
        logger.debug(log_json(self.req_context, logging.DEBUG, "api_config: " + str(api_config)))
        return api_config[self.name]["url"], api_config[self.name]["type"]

    def set_api_url(self, key, val):
        strx = self.url
        strx = strx.replace("$" + str(key), str(val))
        logger.debug(log_json(self.req_context, logging.DEBUG, "url replace var: " + strx))
        self.url = strx
        return self.url

    def set_api_query(self, request):
        strx = self.url
        query = request.META['QUERY_STRING']
        if "?" in self.url:
            strx = strx + "&" + query
        else:
            strx = strx + "?" + query
        logger.debug(log_json(self.req_context, logging.DEBUG, "url add query: " + strx))
        self.url = strx
        return self.url

    def set_api_params(self, params):
        strx = self.url
        if "?" in self.url:
            strx = strx + "&" + params
        else:
            strx = strx + "?" + params
        logger.debug(log_json(self.req_context, logging.DEBUG, "url add query: " + strx))
        self.url = strx
        return self.url

    def process(self, method, url, data=None, headers=None):
        try:
            logger.debug(log_json(self.req_context, logging.DEBUG, "method: " + str(method) + " url: " + str(url)))
            now = datetime.datetime.now()
            ret = exec_client(self.req_context, method, url, self.api_type, data=data, headers=headers)
            total = datetime.datetime.now() - now
            logger.info(log_json(self.req_context, logging.INFO, "performance",
                                 {"type": "API", "milliseconds": int(total.total_seconds() * 1000), "url": str(url)}))
            logger.debug(log_json(self.req_context, logging.DEBUG, "ret: " + str(ret)))
            return ret
        except requests.ConnectionError as e:
            msg = str(e)
            logger.debug("error: " + msg)
            ret = ApiError(msg)
            ret.status_code = -1
            raise ret
        except requests.HTTPError as e:
            msg = str(e)
            logger.debug("error: " + msg)
            ret = ApiError(msg)
            ret.status_code = -2
            raise ret
        except requests.Timeout as e:
            msg = str(e)
            logger.debug("error: " + msg)
            ret = ApiError(msg)
            ret.status_code = -3
            raise ret
        except requests.RequestException as e:
            msg = str(e)
            logger.debug("error: " + msg)
            ret = ApiError(msg)
            ret.status_code = -4
            raise ret

    def get(self, headers=None):
        if headers is None:
            headers = headers
        return self.process('GET', self.url, headers=headers)

    def post(self, data, headers=None):
        if headers is None:
            headers = headers
        return self.process('POST', self.url, data=data, headers=headers)

    def put(self, data, headers=None):
        if headers is None:
            headers = headers
        return self.process('PUT', self.url, data=data, headers=headers)

    def patch(self, data, headers=None):
        if headers is None:
            headers = headers
        return self.process('PATCH', self.url, data=data, headers=headers)

    def delete(self, headers=None):
        if headers is None:
            headers = headers
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


def call_lambda(func_name, event):
    client = boto3.client('lambda', region_name=settings.AWS_REGION)
    ret = client.invoke(
        FunctionName=func_name,
        InvocationType='RequestResponse',
        LogType='None',
        Payload=bytes(json.dumps(event))
    )
    return ret


class ApiLambda(object):
    pass


##################################### test #########################


class ApiTest(AbsBaseApi):
    name = 'Google'
