import logging

from enum import Enum

logger = logging.getLogger(__name__)


class HTTPChoice(Enum):  # A subclass of Enum
    get = "get"
    post = "post"
    put = "put"
    delete = "delete"
    patch = "patch"
