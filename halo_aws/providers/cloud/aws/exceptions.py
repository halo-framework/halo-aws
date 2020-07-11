from __future__ import print_function

from abc import ABCMeta

class HaloAwsException(Exception):
    __metaclass__ = ABCMeta
    """The abstract Generic exception for halo"""

    def __init__(self, message, original_exception=None, detail=None,data=None):
        super(HaloAwsException, self).__init__()
        self.message = message
        self.original_exception = original_exception
        self.detail = detail
        self.data = data

    def __str__(self):
        msg = str(self.message)
        if self.original_exception:
            msg = msg + " ,original:" +str(self.original_exception)
        return msg  # __str__() obviously expects a string to be returned, so make sure not to send any other data types

class HaloAwsError(HaloAwsException):
    __metaclass__ = ABCMeta
    pass

class ProviderError(HaloAwsError):
    pass

class DbError(HaloAwsError):
    pass


class DbIdemError(DbError):
    pass

class ApiTimeOutExpiredError(HaloAwsError):
    pass
