from __future__ import print_function

# python
import datetime
import logging
import os
import re
import time
import uuid

import requests
# django
from django.conf import settings

from .exceptions import MaxTryHookException

# DRF

"""
[DEBUG]	2018-07-04T14:43:13.413Z	943ecbc5-7f98-11e8-b37a-5f5dcef64369	APIG: 946fe9db-d4bd-42ec-b0b8-33c701d8f2e2 - environ: 
{'DYNAMODB_URL': 'http://dynamodb.us-east-1.amazonaws.com', '_HANDLER': 'trader1service.handler.lambda_handler', 'AWS_LAMBDA_FUNCTION_VERSION': '$LATEST', 
'FUNC_NAME': 'trader1', u'SERVERTYPE': u'AWS Lambda', 'REDIS_URL': 'rediscache://127.0.0.1:6379/1?client_class=django_redis.client.DefaultClient&password=redis-un-githubbed-password', 
'EXTENSION_URL': 'https://chrome.google.com/webstore/detail/upc-almost-real-time-pric/pkegapagjeenhnhkdmnbkdinffimjmop?hl=en', 
'LAMBDA_TASK_ROOT': '/var/task', 'EXTENSION_ID': 'pkegapagjeenhnhkdmnbkdinffimjmop', 'PATH': '/usr/local/bin:/usr/bin/:/bin', 
'SECRET_KEY': 'z-ba%0c2@udmxs^jrnc(6h-2ukp#g2f34ufo2ks%hrl6pr9z92', 'LD_LIBRARY_PATH': '/lib64:/usr/lib64:/var/runtime:/var/runtime/lib:/var/task:/var/task/lib', 
'LANG': 'en_US.UTF-8', 'TZ': 'America/Chicago', 'SERVER_NAME': 'dev.rtpricer.com', 'AWS_REGION': u'us-east-1', 'AWS_XRAY_CONTEXT_MISSING': 'LOG_ERROR', 
u'FRAMEWORK': u'Zappa', 'AWS_SESSION_TOKEN': 'FQoDYXdzEHYaDPOwF1KU/LgH/Okq/SLkAaYdQteWR6Getm+XB3Ngk1Veb1zaSKz9DzFX9aEMxywxypMsw2ZcU2A/haVSOrCHokPkIsi1P7cb2vr7PlIr5digKgVzchyxTHzNOxDYMWP3yJdvFNfIJ/ydAySNLr/7wGI6GiqXFJSzHuXTsPXoYw8dicMxJ1NY6ru5qSiaD0vDSbV/b+4jVTa2OUX1WLr7WKozTZ40cs/K2Lngc8M3wYn4xj/vq+1Zw93+wU4R51T0FILRlUtqKMHdyq+JxpS5x9hWL494kNXZhrLRdTCybdfJ/+SVRJvNPHGenLcm/O6pHtRZnCiHhPPZBQ==', 
'AWS_SECURITY_TOKEN': 'FQoDYXdzEHYaDPOwF1KU/LgH/Okq/SLkAaYdQteWR6Getm+XB3Ngk1Veb1zaSKz9DzFX9aEMxywxypMsw2ZcU2A/haVSOrCHokPkIsi1P7cb2vr7PlIr5digKgVzchyxTHzNOxDYMWP3yJdvFNfIJ/ydAySNLr/7wGI6GiqXFJSzHuXTsPXoYw8dicMxJ1NY6ru5qSiaD0vDSbV/b+4jVTa2OUX1WLr7WKozTZ40cs/K2Lngc8M3wYn4xj/vq+1Zw93+wU4R51T0FILRlUtqKMHdyq+JxpS5x9hWL494kNXZhrLRdTCybdfJ/+SVRJvNPHGenLcm/O6pHtRZnCiHhPPZBQ==', 
'LAMBDA_RUNTIME_DIR': '/var/runtime', 'PYTHONPATH': '/var/runtime', 'EMAIL_BACKEND': 'django_ses.SESBackend', 'CACHE_URL': 'LocMemCache:///mem', 
u'STAGE': 'dev', 'RC_SECRET_KEY': '6LdnDVcUAAAAAHZVqhLkqLPDF1Hv98ZfibjUIyF0', 'SERVER_LOCAL': 'False', 'STATIC_S3': 'https://s3.amazonaws.com/rtpricer-static/', 
'AWS_LAMBDA_FUNCTION_MEMORY_SIZE': '512', 'SITE_NAME': 'rtpricer.com', 'GA_KEY': 'UA-112752698-2', '_AWS_XRAY_DAEMON_PORT': '2000', 
'_AWS_XRAY_DAEMON_ADDRESS': '169.254.79.2', 'AWS_LAMBDA_LOG_GROUP_NAME': '/aws/lambda/trader1-dev', 'RC_SITE_KEY': '6LdnDVcUAAAAAAChI95HebUvozeZNv7C526nTTDK', 
'DB_VER': '53', 'LOADER_URL': 'https://uw8f0cxo9b.execute-api.us-east-1.amazonaws.com', u'PROJECT': 'trader1', 'DEBUG': 'True', 
'AWS_LAMBDA_LOG_STREAM_NAME': '2018/07/04/[$LATEST]dac7fcd2302f475e84e2efcc14016cff', 'AWS_ACCESS_KEY_ID': 'ASIAIU3RDZ73KXAZT3BA', 
'_X_AMZN_TRACE_ID': 'Root=1-5b3cdd01-9c0d16e2050e40b43ac309c4;Parent=589ee38f0e8efebb;Sampled=0', 'EXTENSION_VER': '0.9', 'AWS_DEFAULT_REGION': 'us-east-1', 
'DJANGO_CONFIGURATION': 'dev', 'DATABASE_URL': 'sqlite:////tmp/db.sqlite3', 'DJANGO_SETTINGS_MODULE': 'trader1service.settings', 
'AWS_SECRET_ACCESS_KEY': '+MV8E2v9VSXTcGTmyvSBrq+S6983i7+Ae7E+dWm+', 'AWS_EXECUTION_ENV': 'AWS_Lambda_python2.7', 'AWS_XRAY_DAEMON_ADDRESS': '169.254.79.2:2000', 
'SECRET_JWT_KEY': '1234567890', 'AWS_LAMBDA_FUNCTION_NAME': 'trader1-dev'}

[DEBUG]	2018-07-04T15:45:41.526Z	4e4dbe1e-7fa1-11e8-8cbc-15a56cf14c11 APIG: 00723a49-2ee7-49bc-b8e8-2a791cb3c773 - headers: {u'HTTP_X_AMZN_TRACE_ID': 'Root=1-5b3ceba5-c1603c1fb3c31bff03ecba11', 
u'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest', u'HTTP_CLOUDFRONT_IS_DESKTOP_VIEWER': 'true', u'HTTP_X_FORWARDED_PROTO': 'https', u'wsgi.multithread': False, 
u'HTTP_X_AMZ_CF_ID': 'LowGhW59Iycq_--oS2AFaRuQ8KeFvMR3zsqIB_hKFEtfkqZruxrp8g==', u'HTTP_CLOUDFRONT_VIEWER_COUNTRY': 'IL', u'SCRIPT_NAME': u'/dev', u'wsgi.input': None, 
u'REQUEST_METHOD': u'GET', u'HTTP_HOST': '3oktz7m6j2.execute-api.us-east-1.amazonaws.com', u'PATH_INFO': u'/top/', u'HTTPS': u'on', u'SERVER_PROTOCOL': 'HTTP/1.1', 
u'QUERY_STRING': 'skip=0&search=&limit=5&_=1530719134240', u'HTTP_CLOUDFRONT_IS_TABLET_VIEWER': 'false', u'HTTP_ACCEPT': '*/*', u'HTTP_CLOUDFRONT_FORWARDED_PROTO': 'https', 
u'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36', u'wsgi.version': (1, 0), 
u'HTTP_COOKIE': '__atuvc=28%7C27; _ga=GA1.4.758072209.1516522643; _gid=GA1.4.252116172.1530566741', u'SERVER_NAME': 'zappa', u'REMOTE_ADDR': u'62.219.237.170', 
u'wsgi.run_once': False, u'wsgi.errors': <__main__.CustomFile object at 0x7f4e5ad56450>, u'wsgi.multiprocess': False, u'HTTP_ACCEPT_LANGUAGE': 'en-US,
en;q=0.9,fr;q=0.8,fr-FR;q=0.7,he-IL;q=0.6,he;q=0.5', u'HTTP_CLOUDFRONT_IS_MOBILE_VIEWER': 'false', u'wsgi.url_scheme': u'https', 
u'HTTP_VIA': '2.0 e4a44efc4b3241dc23019df63a1f645c.cloudfront.net (CloudFront)', u'HTTP_X_FORWARDED_PORT': '443', 
u'HTTP_CLOUDFRONT_IS_SMARTTV_VIEWER': 'false', u'SERVER_PORT': u'443', u'HTTP_X_FORWARDED_FOR': '62.219.237.170, 54.182.239.100', 
u'HTTP_REFERER': 'https://3oktz7m6j2.execute-api.us-east-1.amazonaws.com/dev', u'lambda.context': <__main__.LambdaContext object at 0x7f4e589e3ed0>, 
u'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br'}
"""

logger = logging.getLogger(__name__)

def strx(str1):
	if str1:
		try:
			return str1.encode('utf-8').strip()
		except Exception as e:
			return str(str1)
		except AttributeError as e:
			return str(str1)
	return ''


class Util:

	def __init__(self):
		pass

	logprefix = None

	@staticmethod
	def mobile(request):
		"""Return True if the request comes from a mobile device."""

		MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

		if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
			return True
		else:
			return False

	@staticmethod
	def get_chrome_browser(request):

		CHROME_AGENT_RE = re.compile(r".*(Chrome)", re.IGNORECASE)
		NON_CHROME_AGENT_RE = re.compile(
			r".*(Aviator | ChromePlus | coc_ | Dragon | Edge | Flock | Iron | Kinza | Maxthon | MxNitro | Nichrome | OPR | Perk | Rockmelt | Seznam | Sleipnir | Spark | UBrowser | Vivaldi | WebExplorer | YaBrowser)",
			re.IGNORECASE)

		if CHROME_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
			if NON_CHROME_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
				return False
			else:
				return True
		else:
			return False

	@staticmethod
	def check_if_robot():
		return False

	################################################################################################3

	@staticmethod
	def get_lambda_context(request):
		# AWS_REGION
		# AWS_LAMBDA_FUNCTION_NAME
		# 'lambda.context'
		# x-amzn-RequestId
		if 'lambda.context' in request.META:
			return request.META['lambda.context']
		else:
			return None

	@staticmethod
	def get_aws_request_id(request):
		context = Util.get_lambda_context(request)
		if context:
			return context.aws_request_id
		return uuid.uuid4().__str__()

	@staticmethod
	def get_func_name():
		if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
			return os.environ['AWS_LAMBDA_FUNCTION_NAME']
		else:
			return settings.FUNC_NAME

	@staticmethod
	def get_correlation_id(request):
		if "HTTP_X_CORRELATION_ID" in request.META:
			x_correlation_id = request.META["HTTP_X_CORRELATION_ID"]
		else:
			x_correlation_id = Util.get_aws_request_id(request)
		return x_correlation_id

	@staticmethod
	def get_user_agent(request):
		if "HTTP_X_USER_AGENT" in request.META:
			user_agent = request.META["HTTP_X_USER_AGENT"]
		else:
			user_agent = Util.get_func_name() + ':' + request.path + ':' + request.method + ':' + settings.INSTANCE_ID
		return user_agent

	@staticmethod
	def get_req_context(request, api_key=None):
		x_correlation_id = Util.get_correlation_id(request)
		x_user_agent = Util.get_user_agent(request)
		if "HTTP_DEBUG_LOG_ENABLED" in request.META:
			dlog = request.META["HTTP_DEBUG_LOG_ENABLED"]
		else:
			dlog = 'false'
		ret = {"x-user-agent": x_user_agent, "aws_request_id": Util.get_aws_request_id(request),
			   "x-correlation-id": x_correlation_id, "debug-log-enabled": dlog}
		if api_key:
			ret["x-api-key"] = api_key
		return ret

	@staticmethod
	def get_headers(request):
		regex_http_ = re.compile(r'^HTTP_.+$')
		regex_content_type = re.compile(r'^CONTENT_TYPE$')
		regex_content_length = re.compile(r'^CONTENT_LENGTH$')
		request_headers = {}
		for header in request.META:
			if regex_http_.match(header) or regex_content_type.match(header) or regex_content_length.match(header):
				request_headers[header] = request.META[header]
		return request_headers

	@staticmethod
	def isDebugEnabled(request, req_context):
		# disable debug logging by default, but allow override via env variables
		# or if enabled via forwarded request context
		if settings.DEBUG:
			return True
		if req_context["Debug-Log-Enabled"] == 'true':
			epoch = datetime.datetime.utcfromtimestamp(0)
			seconds = int((datetime.datetime.now() - epoch).total_seconds())
			if seconds % 20:
				return True
		return False

	@staticmethod
	def get_auth_context(request, key=None):
		return {}

	@staticmethod
	def get_correlation_from_event(event):
		if Util.logprefix:
			print("cached logprefix " + Util.logprefix)
			return Util.logprefix
		correlate_id = ''
		user_agent = ''
		# from api gateway
		if "httpMethod" in event and "requestContext" in event:
			if "headers" in event:
				headers = event["headers"]
				# get correlation-id
				if "x-correlation-id" in headers:
					correlate_id = headers["x-correlation-id"]
				else:
					if "aws_request_id" in headers:
						correlate_id = headers["aws_request_id"]
					else:
						correlate_id = uuid.uuid4().__str__()
				# get user-agent = get_func_name + ':' + path + ':' + request.method + ':' + host_ip
				if "x-user-agent" in headers:
					user_agent = headers["x-user-agent"]
				else:
					if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
						func_name = os.environ['AWS_LAMBDA_FUNCTION_NAME']
					else:
						if "apiId" in event["requestContext"]:
							func_name = event["requestContext"]["apiId"]
						else:
							func_name = headers["Host"]
					if "path" in event["requestContext"]:
						path = event["requestContext"]["path"]
					else:
						path = "path"
					if "httpMethod" in event:
						method = event["httpMethod"]
					else:
						if "httpMethod" in event["requestContext"]:
							method = event["requestContext"]["httpMethod"]
						else:
							method = "method"
					host_ip = "12.34.56.78"
					user_agent = func_name + ':' + path + ':' + method + ':' + host_ip
		# from other source
		else:
			if "x-correlation-id" in event:
				correlate_id = event["x-correlation-id"]
			if "x-user-agent" in event:
				user_agent = event["x-user-agent"]
			if "Debug-Log-Enabled" in event:
				debug_flag = event["Debug-Log-Enabled"]
		logprefix = user_agent + " " + correlate_id
		Util.logprefix = logprefix
		return logprefix

	@staticmethod
	def get_return_code_tag(request):
		tag = "tag"
		if "x-code-tag-id" in request.META:
			tag = request.META["x-code-tag-id"]
		return tag

	@staticmethod
	def send_hook(method, url, data=None, headers=None):
		msg = "can not send hook"
		for i in range(0, settings.HTTP_MAX_RETRY):
			try:
				logger.debug("try " + str(i))
				ret = requests.request(method, url, data=data, headers=headers, timeout=settings.HOOK_TIMEOUT_IN_MS)
				if ret.status_code == 500 or ret.status_code == 502 or ret.status_code == 504:
					if i > 0:
						time.sleep(settings.HTTP_RETRY_SLEEP)
					continue
				return ret
			except Exception as e:
				emsg = str(e)
				logger.debug("Exception in method=" + method + " " + emsg)
				if i > 0:
					time.sleep(settings.HTTP_RETRY_SLEEP)
				continue
		raise MaxTryHookException(msg)

	@staticmethod
	def get_client_ip(request):  # front - when browser calls us
		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = request.META.get('REMOTE_ADDR')
		return ip

	@staticmethod
	def get_server_client_ip(request):  #not front - when service calls us
		return request.META.get('HTTP_REFERER')

	@staticmethod
	def get_hook_url(request, correlate_id, uagent):
		env = "/dev"
		port = "80"
		base_url = None
		host = "host"
		return_code_tag = Util.get_return_code_tag(request)
		if 'HTTP_REFERER' in request.META:
			base_url = request.META['HTTP_REFERER']
		if base_url is None and 'HTTP_HOST' in request.META:
			host = request.META['HTTP_HOST']
			base_url = "https://" + host + env
		if base_url is None:
			base_url = "https://" + host + ":" + port + env
		url = base_url + "/hook?reqid=" + correlate_id + "&uagent=" + uagent + "&tag=" + return_code_tag
		logger.debug("in send_hook_back " + url)
		return url

	@staticmethod
	def terminate_action(correlate_id, error_message):
		print("terminate_action")
		return
