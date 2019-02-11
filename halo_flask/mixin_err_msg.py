#!/usr/bin/env python
import logging

# from cStringIO import StringIO
# aws
# common


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

    # hashx["ApiException"] = {"code": 114, "message": "Server Error"}

    def get_code(self,ex):
        """
        get the proper status code and error msg for exception
        :param ex:
        :return:
        """
        e = type(ex).__name__
        emsg = str(ex)
        logger.debug("e=" + emsg)
        if e in self.hashx:
            code = self.hashx[e]["code"]
            msg = self.hashx[e]["message"]
        else:
            code = 500
            msg = "Server Error"
            if emsg != None and emsg != "":
                msg = emsg
        return code, msg
