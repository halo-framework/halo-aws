from __future__ import print_function

import json
import logging
from enum import Enum

from .util import Util

logger = logging.getLogger(__name__)


class LogLevels(Enum):
    DEBUG = 0,

    INFO = 1,

    WARN = 2,

    ERROR = 3


def append_error(params, err):
    if not err:
        return params
    error = {"errorName": type(err).__name__, "errorMessage": str(err), "stackTrace": err.stack}
    dict_items = dict(params.items() | error.items())
    return dict_items


def log_json(req_context, levelName, message, params, err=None):
    if levelName == 'DEBUG' and not Util.isDebugEnabled(req_context):
        return None

    context = Util.get_context()
    dict_items = dict(req_context.items() + context.items())
    logMsg = {key: value for (key, value) in (dict_items.items())}
    logMsg['level'] = levelName
    logMsg['message'] = message
    pe = append_error(params, err)
    if pe:
        logMsg['params'] = pe

    print(json.dumps(logMsg))
    return logMsg
    # {"aws_request_id": "1fcf5a10-9d44-49dd-bbad-9f23945c306f", "level": "DEBUG", "x-user-agent": "halolib:/:GET:f55a", "awsRegion": "REGION", "x-correlation-id": "1f271213-6d32-40b7-b1dc-12e3a9a31bf4", "debug-log-enabled": "false", "functionVersion": "VER", "message": "we did it", "stage": "STAGE", "functionMemorySize": "MEM", "functionName": "halolib"}
