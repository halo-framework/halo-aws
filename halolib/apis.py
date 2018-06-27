# Create your mixin here.

# python
import logging
from abc import ABCMeta

import requests
# aws
# common
# django
from django.conf import settings

from .exceptions import HaloError, HaloException

# DRF


headers = {
    'User-Agent': settings.headers,
}

logger = logging.getLogger(__name__)

class ApiException(HaloException):
	pass

class ApiError(HaloError):
	pass


class AbsBaseApi(object):
	__metaclass__ = ABCMeta

	url = None

	#def __init__(self,url):
	#	self.url = url

	def set_api_url(self, key,val):
		strx = self.url
		strx = strx.replace("$" + str(key), str(val))
		logger.debug("url replace var: " + strx)
		self.url = strx
		return self.url

	def process(self,method,url,data=None,headers=None):
		try:
			ret = requests.request(str(method),url,data=data,headers=headers)
			logger.debug("ret: " + str(ret))
			return ret
		except requests.ConnectionError, e:
			logger.debug("error: " + str(e.message))
			ret = ApiError(e.message)
			ret.status_code = -1
			return ret
		except requests.HTTPError,e:
			logger.debug("error: " + str(e.message))
			ret = ApiError(e.message)
			ret.status_code = -2
			return ret
		except requests.Timeout,e:
			logger.debug("error: " + str(e.message))
			ret = ApiError(e.message)
			ret.status_code = -3
			return ret
		except requests.RequestException,e:
			logger.debug("error: " + str(e.message))
			ret = ApiError(e.message)
			ret.status_code = -4
			return ret

	def get(self,headers=None):
		return self.process('GET',self.url,headers=headers)

	def post(self, data,headers=None):
		return self.process('POST', self.url,data=data,headers=headers)

	def put(self, data,headers=None):
		return self.process('PUT', self.url,data=data,headers=headers)

	def delete(self,headers=None):
		return self.process('DELETE', self.url,headers=headers)



##################################### test #########################



