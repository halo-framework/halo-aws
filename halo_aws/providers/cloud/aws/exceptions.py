from __future__ import print_function

from abc import ABCMeta

class HaloAwsException(Exception):
    __metaclass__ = ABCMeta
    """
    The exception used when a template does not exist. Accepts the following
    optional arguments:


    """
    def __init__(self, msg, tried=None, backend=None, chain=None):
        super(HaloAwsException, self).__init__(msg)


class HaloAwsError(HaloAwsException):
    __metaclass__ = ABCMeta
    """
    The exception used when a template does not exist. Accepts the following
    optional arguments:


    """
    def __init__(self, msg, tried=None, backend=None, chain=None):
        super(HaloAwsError, self).__init__(msg)



class ProviderError(HaloAwsError):
    pass

class DbError(HaloAwsError):
    pass


class DbIdemError(DbError):
    pass

class ApiTimeOutExpiredError(HaloAwsError):
    pass
