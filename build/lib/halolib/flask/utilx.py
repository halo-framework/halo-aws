from __future__ import print_function

import json
# python
import logging
import re

from flask import Response

from ..base_util import BaseUtil
from ..settingsx import settingsx

settings = settingsx()

logger = logging.getLogger(__name__)


def strx(str1):
    """

    :param str1:
    :return:
    """
    if str1:
        try:
            return str1.encode('utf-8').strip()
        except AttributeError as e:
            return str(str1)
        except Exception as e:
            return str(str1)
    return ''


class Util(BaseUtil):

    @staticmethod
    def get_chrome_browser(request):
        """

        :param request:
        :return:
        """
        CHROME_AGENT_RE = re.compile(r".*(Chrome)", re.IGNORECASE)
        NON_CHROME_AGENT_RE = re.compile(
            r".*(Aviator | ChromePlus | coc_ | Dragon | Edge | Flock | Iron | Kinza | Maxthon | MxNitro | Nichrome | OPR | Perk | Rockmelt | Seznam | Sleipnir | Spark | UBrowser | Vivaldi | WebExplorer | YaBrowser)",
            re.IGNORECASE)

        if CHROME_AGENT_RE.match(request.headers['HTTP_USER_AGENT']):
            if NON_CHROME_AGENT_RE.match(request.headers['HTTP_USER_AGENT']):
                return False
            else:
                return True
        else:
            return False

    @staticmethod
    def mobile(request):
        """Return True if the request comes from a mobile device.
        :param request:
        :return:
        """

        MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

        if MOBILE_AGENT_RE.match(request.headers['HTTP_USER_AGENT']):
            return True
        else:
            return False

    @staticmethod
    def get_lambda_context(request):
        """

        :param request:
        :return:
        """
        # AWS_REGION
        # AWS_LAMBDA_FUNCTION_NAME
        # 'lambda.context'
        # x-amzn-RequestId
        if 'lambda.context' in request.headers:
            return request.headers['lambda.context']
        elif 'context' in request.headers:
            return request.headers['context']
        else:
            return None

    @classmethod
    def get_correlation_id(cls, request):
        """

        :param request:
        :return:
        """
        if "HTTP_X_CORRELATION_ID" in request.headers:
            x_correlation_id = request.headers["HTTP_X_CORRELATION_ID"]
        else:
            x_correlation_id = cls.get_aws_request_id(request)
        return x_correlation_id

    @classmethod
    def get_user_agent(cls, request):
        """

        :param request:
        :return:
        """
        if "HTTP_X_USER_AGENT" in request.headers:
            user_agent = request.headers["HTTP_X_USER_AGENT"]
        else:
            user_agent = cls.get_func_name() + ':' + request.path + ':' + request.method + ':' + settings.INSTANCE_ID
        return user_agent

    @classmethod
    def get_debug_enabled(cls, request):
        """

        :param request:
        :return:
        """
        # check if the specific call is debug enabled
        if "HTTP_DEBUG_LOG_ENABLED" in request.headers:
            dlog = request.headers["HTTP_DEBUG_LOG_ENABLED"]
            if dlog == 'true':
                return 'true'
        # check if system wide enabled - done on edge
        if "HTTP_X_CORRELATION_ID" not in request.headers:
            dlog = cls.get_system_debug_enabled()
            if dlog == 'true':
                return 'true'
        return 'false'

    @staticmethod
    def get_headers(request):
        """

        :param request:
        :return:
        """
        regex_http_ = re.compile(r'^HTTP_.+$')
        regex_content_type = re.compile(r'^CONTENT_TYPE$')
        regex_content_length = re.compile(r'^CONTENT_LENGTH$')
        request_headers = {}
        for header, value in request.headers:
            logger.debug("header=" + str(header))
            if regex_http_.match(header) or regex_content_type.match(header) or regex_content_length.match(header):
                request_headers[header] = value  # request.headers[header]
        return request_headers

    @staticmethod
    def get_return_code_tag(request):
        """

        :param request:
        :return:
        """
        tag = "tag"
        if "x-code-tag-id" in request.headers:
            tag = request.headers["x-code-tag-id"]
        return tag

    @staticmethod
    def get_client_ip(request):  # front - when browser calls us
        """

        :param request:
        :return:
        """
        x_forwarded_for = request.headers.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.headers.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def get_server_client_ip(request):  # not front - when service calls us
        """

        :param request:
        :return:
        """
        return request.headers.get('HTTP_REFERER')

    """"
    Success
    response
    return data
    {
        "data": {
            "id": 1001,
            "name": "Wing"
        }
    }
    Error
    response
    return error
    {
        "error": {
            "code": 404,
            "message": "ID not found",
            "requestId": "123-456"
        }
    }
    """

    @staticmethod
    def json_data_response(data, status_code=200):
        """

        :param data:
        :param status_code:
        :return:
        """
        return Response(json.dumps({"data": data}), status=status_code)

    @staticmethod
    def get_req_params(request):
        """

        :param request:
        :return:
        """
        qd = {}
        if request.method == 'GET':
            qd = request.args
        elif request.method == 'POST':
            qd = request.args
        return qd
