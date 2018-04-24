# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.conf import settings
import json
import os
# Create your views here.

import boto3
from django.core.cache import cache

from django.utils.encoding import smart_str

def _smart_key(key):
    return smart_str(''.join([c for c in key if ord(c) > 32 and ord(c) != 127]))

def make_key(key, key_prefix, version):
    "Truncate all keys to 250 or less and remove control characters"
    return ':'.join([key_prefix, str(version), _smart_key(key)])[:250]

def db_get(hash):
    #print "db_get",urlx
    if hash:
        ret = cache.get(hash)
        #ret = cache.get(make_key(hash, '', 1))
        if ret is not None:
            #print "cache hit",hash
            return ret
    return None

def db_put(hash,score):
    if hash:
        cache.set(hash,score,None)
        #cache.set(make_key(hash, '', 1),score,None)
        #print "cache miss",cache.get(hash)
    else:
        raise Exception('urlx key has no value')
