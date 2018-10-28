#!/usr/bin/env python
import logging

# from cStringIO import StringIO
# aws
# common
# django


logger = logging.getLogger(__name__)


class ErrorMessages(object):
    hashx = {}
    # generic halo messages and proprietery api messages
    TransactionDisabled = msg_00001 = "ERROR-00001: Transaction Requests is disabled in this API instance."
    # custom messages
    hashx["MaxTryException"] = {"code": 123, "message": "Server Error"}
    hashx["ApiError"] = {"code": 111, "message": "Server Error"}
    hashx["ConnectionError"] = {"code": 112, "message": "Server Error"}
    hashx["TypeError"] = {"code": 113, "message": "Server Error"}

    @staticmethod
    def get_code(ex):
        e = type(ex).__name__
        logger.debug("e=" + e)
        if e in ErrorMessages.hashx:
            return ErrorMessages.hashx[e]["code"], ErrorMessages.hashx[e]["message"]
        return 500, "Server Error"
