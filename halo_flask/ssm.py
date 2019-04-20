from __future__ import print_function

import configparser
import datetime
import json
import logging
import os
import time

#@ TODO put_parameter should be activated only is current value is different then the existing one
#@ TODO perf activation will reload SSM if needed and refresh API table

from .ssm_aws import set_app_param_config as set_app_param_config_aws
from .ssm_aws import get_config as get_config_aws
from .ssm_aws import get_app_config as get_app_config_aws
from .ssm_onprem import set_app_param_config as set_app_param_config_onprem
from .ssm_onprem import get_config as get_config_onprem
from .ssm_onprem import get_app_config as get_app_config_onprem

from .exceptions import HaloError, CacheKeyError, CacheExpireError

# from .logs import log_json


current_milli_time = lambda: int(round(time.time() * 1000))

logger = logging.getLogger(__name__)

# Initialize boto3 client at global scope for connection reuse
client = None
env = os.environ['HALO_STAGE']
type = os.environ['HALO_TYPE']
app_config_path = os.environ['HALO_FUNC_NAME']
app_name = os.environ['HALO_APP_NAME']
full_config_path = '/' + app_name + '/' + env + '/' + app_config_path
short_config_path = '/' + app_name + '/' + type + '/service'

AWS = False
if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
    AWS = True

def set_app_param_config(region_name, host):
    """

    :param region_name:
    :param host:
    :return:
    """
    if AWS:
        return set_app_param_config_aws(region_name,host)
    return set_app_param_config_onprem(region_name,host)



def get_config(region_name):
    """

    :param region_name:
    :return:
    """
    # Initialize app if it doesn't yet exist
    if AWS:
        return get_config_aws(region_name)
    return get_config_onprem(region_name)


def get_app_config(region_name):
    """

    :param region_name:
    :return:
    """
    # Initialize app if it doesn't yet exist
    if AWS:
        return get_app_config_aws(region_name)
    return get_app_config_onprem(region_name)
