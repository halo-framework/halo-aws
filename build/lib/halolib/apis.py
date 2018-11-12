from __future__ import print_function

# python
import datetime
import importlib
import logging
import time
from abc import ABCMeta

import requests

from .exceptions import MaxTryHttpException, ApiError
from .logs import log_json
from .settingsx import settingsx

try:
    from .util import Util
except:
    from .flask.utilx import Util

settings = settingsx()

# DRF


headers = {
    'User-Agent': settings.USER_HEADERS,
}

logger = logging.getLogger(__name__)


def exec_client(req_context, method, url, api_type, timeout, data=None, headers=None):
    """

    :param req_context:
    :param method:
    :param url:
    :param api_type:
    :param timeout:
    :param data:
    :param headers:
    :return:
    """
    msg = "Max Try for url: " + str(url)
    for i in range(0, settings.HTTP_MAX_RETRY):
        try:
            logger.debug("try: " + str(i), extra=log_json(req_context))
            ret = requests.request(method, url, data=data, headers=headers,
                                   timeout=timeout)
            logger.debug("status_code=" + str(ret.status_code), extra=log_json(req_context))
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
            logger.debug(
                "ReadTimeout " + str(settings.SERVICE_READ_TIMEOUT_IN_MS) + " in method=" + method + " for url=" + url,
                extra=log_json(req_context))
            if i > 0:
                time.sleep(settings.HTTP_RETRY_SLEEP)
            continue
        except requests.exceptions.ConnectTimeout:
            logger.debug("ConnectTimeout in method=" + str(
                settings.SERVICE_CONNECT_TIMEOUT_IN_MS) + " in method=" + method + " for url=" + url,
                         extra=log_json(req_context))
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
        """

        :return:
        """
        api_config = settings.API_CONFIG
        logger.debug("api_config: " + str(api_config), extra=log_json(self.req_context))
        return api_config[self.name]["url"], api_config[self.name]["type"]

    def set_api_url(self, key, val):
        """

        :param key:
        :param val:
        :return:
        """
        strx = self.url
        strx = strx.replace("$" + str(key), str(val))
        logger.debug("url replace var: " + strx, extra=log_json(self.req_context))
        self.url = strx
        return self.url

    def set_api_query(self, query):
        """

        :param query:
        :return:
        """
        strx = self.url
        if "?" in self.url:
            strx = strx + "&" + query
        else:
            strx = strx + "?" + query
        logger.debug("url add query: " + strx, extra=log_json(self.req_context))
        self.url = strx
        return self.url

    def set_api_params(self, params):
        """

        :param params:
        :return:
        """
        strx = self.url
        if "?" in self.url:
            strx = strx + "&" + params
        else:
            strx = strx + "?" + params
        logger.debug("url add query: " + strx, extra=log_json(self.req_context))
        self.url = strx
        return self.url

    def process(self, method, url, timeout, data=None, headers=None):
        """

        :param method:
        :param url:
        :param timeout:
        :param data:
        :param headers:
        :return:
        """
        try:
            logger.debug("method: " + str(method) + " url: " + str(url), extra=log_json(self.req_context))
            now = datetime.datetime.now()
            ret = exec_client(self.req_context, method, url, self.api_type, timeout, data=data, headers=headers)
            total = datetime.datetime.now() - now
            logger.info("performance_data", extra=log_json(self.req_context,
                                                           {"type": "API",
                                                            "milliseconds": int(total.total_seconds() * 1000),
                                                            "url": str(url)}))
            logger.debug("ret: " + str(ret), extra=log_json(self.req_context))
            return ret
        except requests.ConnectionError as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.req_context))
            er = ApiError(e)
            er.status_code = 500
            raise er
        except requests.HTTPError as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.req_context))
            er = ApiError(e)
            er.status_code = 500
            raise er
        except requests.Timeout as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.req_context))
            er = ApiError(e)
            er.status_code = 500
            raise er
        except requests.RequestException as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.req_context))
            er = ApiError(e)
            er.status_code = 500
            raise er
        except ApiError as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.req_context))
            raise e

    def get(self, timeout, headers=None):
        """

        :param timeout:
        :param headers:
        :return:
        """
        if headers is None:
            headers = headers
        return self.process('GET', self.url, timeout, headers=headers)

    def post(self, data, timeout, headers=None):
        """

        :param data:
        :param timeout:
        :param headers:
        :return:
        """
        logger.debug("payload=" + str(data))
        if headers is None:
            headers = headers
        return self.process('POST', self.url, timeout, data=data, headers=headers)

    def put(self, data, timeout, headers=None):
        """

        :param data:
        :param timeout:
        :param headers:
        :return:
        """
        if headers is None:
            headers = headers
        return self.process('PUT', self.url, timeout, data=data, headers=headers)

    def patch(self, data, timeout, headers=None):
        """

        :param data:
        :param timeout:
        :param headers:
        :return:
        """
        if headers is None:
            headers = headers
        return self.process('PATCH', self.url, timeout, data=data, headers=headers)

    def delete(self, timeout, headers=None):
        """

        :param timeout:
        :param headers:
        :return:
        """
        if headers is None:
            headers = headers
        return self.process('DELETE', self.url, timeout, headers=headers)

    def fwd_process(self, typer, request, vars, headers):
        """

        :param typer:
        :param request:
        :param vars:
        :param headers:
        :return:
        """
        verb = typer.value
        if verb == 'GET' or 'DELETE':
            data = None
        else:
            data = request.data
        return self.process(verb, self.url, Util.get_timeout(request), data=data, headers=headers)


class ApiMngr(object):

    def __init__(self, req_context):
        logger.debug("ApiMngr=" + str(req_context))
        self.req_context = req_context

    @staticmethod
    def get_api(name):
        """

        :param name:
        :return:
        """
        logger.debug("get_api=" + name)
        if name in API_LIST:
            return API_LIST[name]
        return None

    def get_api_instance(self, class_name, **kwargs):
        """

        :param class_name:
        :param kwargs:
        :return:
        """
        logger.debug("get_api_insance=" + class_name)
        module = importlib.import_module(__name__)
        class_ = getattr(module, class_name)
        instance = class_(self.req_context)
        logger.debug("class=" + str(instance))
        return instance


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


class GoogleApi(AbsBaseApi):
    name = 'Google'


API_LIST = {"Google": 'GoogleApi'}
