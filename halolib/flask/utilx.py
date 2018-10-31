from __future__ import print_function

import json
# python
import logging

from flask import Response

from ..base_util import BaseUtil

logger = logging.getLogger(__name__)


class Util(BaseUtil):

    """"
    Success
    response
    return data
    {
        "data": {
            "id": 1001,
            "name": "Wing"
        }
    }
    Error
    response
    return error
    {
        "error": {
            "code": 404,
            "message": "ID not found",
            "requestId": "123-456"
        }
    }
    """

    @staticmethod
    def json_data_response(data, status_code=200):
        return Response(json.dumps({"data": data}), status=status_code)

    @staticmethod
    def get_req_params(request):
        qd = {}
        if request.method == 'GET':
            qd = request.args
        elif request.method == 'POST':
            qd = request.args
        return qd
