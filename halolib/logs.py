from __future__ import print_function

import logging

from .util import Util


def append_error(params, err):
    if not err:
        return params
    stack = None
    if hasattr(err, "stack"):
        stack = err.stack
    error = {"errorName": type(err).__name__, "errorMessage": str(err), "stackTrace": stack}
    dict_items = params.copy()
    dict_items.update(error)
    return dict_items


def log_json(logger, req_context, level, message, params, err=None):
    if level == logging.DEBUG and not Util.isDebugEnabled(req_context):
        return None

    context = Util.get_context()
    dict_items = req_context.copy()
    dict_items.update(context)
    logMsg = {key: value for (key, value) in (dict_items.items())}
    logMsg['level'] = logging.getLevelName(level)
    logMsg['message'] = message
    pe = append_error(params, err)
    if pe:
        logMsg['params'] = pe

    # print(json.dumps(logMsg))
    print("level=" + str(level))
    logger.log(level, logMsg)

    return logMsg
    # {"aws_request_id": "1fcf5a10-9d44-49dd-bbad-9f23945c306f", "level": "DEBUG", "x-user-agent": "halolib:/:GET:f55a", "awsRegion": "REGION", "x-correlation-id": "1f271213-6d32-40b7-b1dc-12e3a9a31bf4", "debug-log-enabled": "false", "functionVersion": "VER", "message": "we did it", "stage": "STAGE", "functionMemorySize": "MEM", "functionName": "halolib"}
