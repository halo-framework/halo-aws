# Create your mixin here.
import os
import sys
import traceback
import datetime
from django.conf import settings
import logging
import uuid
import locale
import jwt
import json
import requests
import hashlib
import urlparse
import boto3
import base64
import re
import urllib

from enum import Enum
from abc import ABCMeta, abstractmethod

from urllib import quote_plus
from django.http import HttpResponse,HttpResponseRedirect
from django.template import Context, loader
from django.contrib import messages
from django.template.exceptions import TemplateDoesNotExist
from django.utils import translation

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework import status



class HaloException(Exception):
    """
    The exception used when a template does not exist. Accepts the following
    optional arguments:


    """
    def __init__(self, msg, tried=None, backend=None, chain=None):
        super(HaloException, self).__init__(msg)


class HaloError(Exception):
    """
    The exception used when a template does not exist. Accepts the following
    optional arguments:


    """
    def __init__(self, msg, tried=None, backend=None, chain=None):
        super(HaloError, self).__init__(msg)