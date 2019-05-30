from __future__ import print_function

# python
import datetime
import importlib
import logging
import time
from abc import ABCMeta,abstractmethod

import requests

from .exceptions import MaxTryHttpException, ApiError
from .logs import log_json
from .settingsx import settingsx


from .flask.utilx import Util

settings = settingsx()

# DRF


headers = {
    'User-Agent': settings.USER_HEADERS,
}

logger = logging.getLogger(__name__)


class AbsBaseClass(object):
    __metaclass__ = ABCMeta

    @classmethod
    def version(self): return "1.0"

    @abstractmethod
    def show(self): raise NotImplementedError

    @abstractmethod
    def show(self): raise NotImplementedError

    @abstractmethod
    def show(self): raise NotImplementedError

    @abstractmethod
    def show(self): raise NotImplementedError



