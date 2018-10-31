from __future__ import print_function

from rest_framework.response import Response

from .base_util import BaseUtil


def strx(str1):
    if str1:
        try:
            return str1.encode('utf-8').strip()
        except AttributeError as e:
            return str(str1)
        except Exception as e:
            return str(str1)
    return ''


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
    def json_data_response(data):
        return Response({"data": data})

    @staticmethod
    def get_req_params(request):
        qd = {}
        if request.method == 'GET':
            qd = request.GET.dict()
        elif request.method == 'POST':
            qd = request.POST.dict()
        return qd
