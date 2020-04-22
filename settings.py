#  settings for  project.

import os
import json

print("start base")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print('BASE_DIR : {}'.format(BASE_DIR))
THE_ENV=os.path.join(BASE_DIR,'env','.env')
print('The .env file has been loaded. env: '+str(THE_ENV))

FUNC_NAME = "FUNC_NAME"
SERVER_LOCAL = True

AWS_REGION = "us-east-1"

###
# Given a version number MAJOR.MINOR.PATCH, increment the:
#
# MAJOR version when you make incompatible  changes,
# MINOR version when you add functionality in a backwards-compatible manner, and
# PATCH version when you make backwards-compatible bug fixes.
###

title = 'webfront'
author = 'Author'
copyright = 'Copyright 2017-2018 ' + author
major = '1'
minor = '1'
patch = '52'
version = major + '.' + minor + '.' + patch
# year.month.day.optional_revision  i.e 2016.05.03 for today
rev = 1
build = '2018.10.10.' + str(rev)
generate = '2018.10.13.19:06:07'
print("generate=" + generate)


def get_version():
    """
    Return package version as listed in  env file
    """
    return version + "/" + build


VERSION = get_version()
print(VERSION)

APPEND_SLASH = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # env.bool('DEBUG', default=True)
print("DEBUG=" + str(DEBUG))

#CACHES = get_cache()

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LOCALE_CODE = 'en-US'
LANGUAGE_CODE = 'en'

LANGUAGES = (
    #('en', _('English')),
    #('nl', _('Dutch')),
    #('he', _('Hebrew')),
)

GET_LANGUAGE = True

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'


PROJECT_APPS = (
    'api',
)

CORS_ORIGIN_ALLOW_ALL = True
#change to proper site in production
#HOME_DOMAIN = env('HOME_DOMAIN')#'amazon.com'
#CORS_ORIGIN_WHITELIST = (
#    HOME_DOMAIN,
#    'localhost:8000',
#    '127.0.0.1:9000'
#)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'main_formatter': {
            'format': '%(levelname)s:%(name)s: %(message)s '
                      '%(asctime)s; %(filename)s:%(lineno)d',
            'datefmt': "%Y-%m-%d %H:%M:%S",
            'class': "pythonjsonlogger.jsonlogger.JsonFormatter",
        },
        'main_formatter_old': {
            'format': '%(levelname)s:%(name)s: %(message)s '
                      '(%(asctime)s; %(filename)s:%(lineno)d)',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
    #    'file': {
    #        'level': 'DEBUG',
    #        'class': 'logging.FileHandler',
    #        'filename': '/path/to/django/debug.log',
    #    },
        #    'console': {
        #        'level': 'ERROR',
        #        'filters': ['require_debug_false'],
        #        'class': 'logging.StreamHandler',
        #        'formatter': 'main_formatter',
        #    },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
        'console_debug_false': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': True,
        },
        'halo_flask.halo_flask.views': {
            'level': 'INFO',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.halo_flask.apis': {
            'level': 'INFO',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.halo_flask.events': {
            'level': 'INFO',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.halo_flask.mixin': {
            'level': 'INFO',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.halo_flask.models': {
            'level': 'INFO',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.halo_flask.util': {
            'level': 'INFO',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.halo_flask.ssm': {
            'level': 'INFO',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
    },
}

USER_HEADERS = 'Mozilla/5.0'

MIXIN_HANDLER = 'loader1service.api.mixin.mixin_handler'

SERVICE_READ_TIMEOUT_IN_SC = 3  # in seconds = 300 ms

SERVICE_CONNECT_TIMEOUT_IN_SC = 3  # in seconds = 300 ms

RECOVER_TIMEOUT_IN_SC = 0.5  # in seconds = 500 ms

MINIMUM_SERVICE_TIMEOUT_IN_SC = 0.1  # in seconds = 100 ms

HTTP_MAX_RETRY = 4

THRIFT_MAX_RETRY = 4

HTTP_RETRY_SLEEP = 10 #0.100  # in seconds = 100 ms

FRONT_WEB = False

FRONT_API = False

import uuid

INSTANCE_ID = uuid.uuid4().__str__()[0:4]

LOG_SAMPLE_RATE = 0.05  # 5%

#ERR_MSG_CLASS = 'halo_flask.mixin_err_msg'


#######################################################################################3



print('The settings file has been loaded.')
