from __future__ import print_function

import logging

logger = logging.getLogger(__name__)


class HaloResponse:

    payload = 'this is HaloResponse'
    code = 200
    headers = []

    def __init__(self, payload=None, code=None, headers=None):
        if payload:
            self.payload = payload
        if code:
            self.code = code
        if headers:
            self.headers = headers
