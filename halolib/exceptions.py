from __future__ import print_function

class HaloException(Exception):
    """
    The exception used when a template does not exist. Accepts the following
    optional arguments:


    """
    def __init__(self, msg, tried=None, backend=None, chain=None):
        super(HaloException, self).__init__(msg)


class HaloError(HaloException):
    """
    The exception used when a template does not exist. Accepts the following
    optional arguments:


    """
    def __init__(self, msg, tried=None, backend=None, chain=None):
        super(HaloError, self).__init__(msg)


class ApiException(HaloException):
    pass


class AuthException(HaloException):
    pass


class MaxTryException(ApiException):
    pass


class MaxTryHttpException(MaxTryException):
    pass


class MaxTryThriftException(MaxTryException):
    pass


class MaxTryHookException(ApiException):
    pass


class NoReturnApiException(HaloException):
    pass
