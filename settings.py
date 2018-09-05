# Django settings for checkerservice project.


import os

import environ
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print('BASE_DIR : {}'.format(BASE_DIR))

root = environ.Path(__file__) - 2 # two folders back (/a/b/ - 2 = /)
env = environ.Env(DEBUG=(bool, False),)

# Operating System Environment variables have precedence over variables defined in the .env file,
# that is to say variables from the .env files will only be used if not defined
# as environment variables.
env_file=root('.env')
print('Loading : {}'.format(env_file))
#with open(env_file, "r") as f:
#    data = f.read()
#    print data
env.read_env(env_file)
print('The .env file has been loaded. env: '+env.str('ENV_NAME'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/


LOC = "loc"
DEV = "dev"
TST = "tst"
PRD = "prd"
ENV_NAME = LOC  # env.str('ENV_NAME')

FUNC_NAME = env.str('FUNC_NAME')

SERVER_LOCAL = True
DB_URL = env('DYNAMODB_LOCAL_URL')
if 'SERVERTYPE' in os.environ and os.environ['SERVERTYPE'] == 'AWS Lambda':
    DB_URL = env('DYNAMODB_URL')
    SERVER_LOCAL = False

# SECURITY WARNING: keep the secret key used in production secret!
# Make this unique, and don't share it with anybody.
SECRET_KEY = env('SECRET_KEY')

APPEND_SLASH = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=True)

SERVER = env('SERVER_NAME')
ALLOWED_HOSTS = ['*','127.0.0.1',SERVER]

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DB_VER = env('DB_VER')
PAGE_SIZE = env.int('PAGE_SIZE', default=5)
DATABASES = {
    'default': env.db(),
}

def get_cache():
  return {
      'default': env.cache()
    }

CACHES = get_cache()

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
    ('en', _('English')),
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


MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'halolib.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django.contrib.staticfiles',
	
	## 3rd party
    'rest_framework',
    'rest_framework_swagger',
    'rest_framework.authtoken',

    ## custom
    'halolib',

    # testing etc:
    'django_jenkins',
    'django_extensions',
    'corsheaders',
)

# CUSTOM AUTH
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

## REST
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        ## we need this for the browsable API to work
        'rest_framework.authentication.SessionAuthentication',
    )
}

# Services:

## Service base urls without a trailing slash:
USER_SERVICE_BASE_URL = 'http://staging.userservice.tangentme.com'

JENKINS_TASKS = (
    'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.with_coverage',
    # 'django_jenkins.tasks.run_sloccount',
    # 'django_jenkins.tasks.run_graphmodels'
)

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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATIC_URL = '/static1/'

STATIC_ROOT = os.path.join(BASE_DIR, "halolib/api/static")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    '/var/www/static/',
]

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
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
    },
    'loggers': {
        'django.request':         {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django':                 {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'root':                   {
            'handlers': ['console'],
            'level': "DEBUG",
        },
        'halolib.halolib.views':  {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'halolib.views':          {
            'level':    'DEBUG',
            'handlers': ['console']
        },
        'halolib.halolib.models': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'halolib.halolib.mixin':  {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'halolib.halolib.apis': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'halolib.halolib.util': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
    },
}

USER_HEADERS = 'Mozilla/5.0'

MIXIN_HANDLER = 'loader1service.api.mixin.mixin_handler'

SERVICE_TIMEOUT_IN_MS = 3  # in seconds

HTTP_MAX_RETRY = 4

THRIFT_MAX_RETRY = 4

HTTP_RETRY_SLEEP = 0.300  # in seconds

SERVICE_NO_RETURN = True

if SERVICE_NO_RETURN:
    SERVICE_TIMEOUT_IN_MS = 0.001

#######################################################################################3

import json

API_CONFIG = None
API_SETTINGS = ENV_NAME + '_api_settings.json'

file_dir = os.path.dirname(__file__)
file_path = os.path.join(file_dir, API_SETTINGS)
with open(file_path, 'r') as fi:
    API_CONFIG = json.load(fi)
    print("api_config:" + str(API_CONFIG))

file_dir = os.path.dirname(__file__)
file_path = os.path.join(file_dir, 'loc_settings.json')
with open(file_path, 'r') as fi:
    LOC_TABLE = json.load(fi)
    print("loc_settings:" + str(LOC_TABLE))

import uuid

INSTANCE_ID = uuid.uuid4().__str__()[0:4]

print('The settings file has been loaded.')
