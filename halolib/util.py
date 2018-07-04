#
# python
import os
import re
import uuid

# django
from django.conf import settings


# DRF

def strx(str1):
    if str1:
        try:
            return str1.encode('utf-8').strip()
        except Exception, e:
            return str(str1)
        except AttributeError, e:
            return str(str1)
    return ''


class Util:

    @staticmethod
    def mobile(request):
        """Return True if the request comes from a mobile device."""

        MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

        if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
            return True
        else:
            return False

    @staticmethod
    def get_chrome_browser(request):

        CHROME_AGENT_RE = re.compile(r".*(Chrome)", re.IGNORECASE)
        NON_CHROME_AGENT_RE = re.compile(
            r".*(Aviator | ChromePlus | coc_ | Dragon | Edge | Flock | Iron | Kinza | Maxthon | MxNitro | Nichrome | OPR | Perk | Rockmelt | Seznam | Sleipnir | Spark | UBrowser | Vivaldi | WebExplorer | YaBrowser)",
            re.IGNORECASE)

        if CHROME_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
            if NON_CHROME_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
                return False
            else:
                return True
        else:
            return False

    @staticmethod
    def check_if_robot():
        return False

    @staticmethod
    def get_lambda_context():
        # AWS_REGION
        # AWS_LAMBDA_FUNCTION_NAME
        # 'lambda.context'
        # x-amzn-RequestId
        if 'lambda.context' in os.environ:
            return os.environ['lambda.context']
        else:
            return None

    @staticmethod
    def get_api_request_id():
        if 'x-amzn-RequestId' in os.environ:
            return os.environ['x-amzn-RequestId']
        return uuid.uuid4().__str__()

    @staticmethod
    def get_aws_request_id():
        context = Util.get_lambda_context()
        if context:
            return context.aws_request_id
        return uuid.uuid4().__str__()

    @staticmethod
    def get_func_name():
        if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
            return os.environ['AWS_LAMBDA_FUNCTION_NAME']
        else:
            return None

    @staticmethod
    def get_context(typer, class_name):
        return {"User-Agent": settings.FUNC_NAME + ':' + class_name + ':' + typer.value,
                "Correlate-ID": Util.get_api_request_id()}
