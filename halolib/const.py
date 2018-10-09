from __future__ import print_function

import logging
from enum import Enum

logger = logging.getLogger(__name__)


class HTTPChoice(Enum):  # A subclass of Enum
    get = "GET"
    post = "POST"
    put = "PUT"
    delete = "DELETE"
    patch = "PATCH"


from django.conf import settings


class settingsx(object):

    def __getattribute__(self, name):
        attr = settings.__getattr__(name)
        if hasattr(attr, '__call__'):
            return attr
        else:
            return attr
