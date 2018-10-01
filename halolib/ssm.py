from __future__ import print_function

import configparser
import json
import logging
import os
import traceback

import boto3
from django.conf import settings

from .logs import log_json

logger = logging.getLogger(__name__)

# Initialize boto3 client at global scope for connection reuse
client = boto3.client('ssm', region_name=settings.AWS_REGION)
env = os.environ['STAGE']
app_config_path = os.environ['APP_CONFIG_PATH']
app_name = os.environ['APP_NAME']
full_config_path = '/' + app_name + '/' + env + '/' + app_config_path
short_config_path = '/' + app_name + '/' + env
# Initialize app at global scope for reuse across invocations
myconfig = None
appconfig = None


class MyConfig:
    def __init__(self, config):
        """
        Construct new MyApp with configuration
        :param config: application configuration
        """
        self.config = config

    def get_config(self):
        return self.config


def load_config(ssm_parameter_path):
    """
    Load configparser from config stored in SSM Parameter Store
    :param ssm_parameter_path: Path to app config in SSM Parameter Store
    :return: ConfigParser holding loaded config
    """
    configuration = configparser.ConfigParser()
    try:
        # Get all parameters for this app
        param_details = client.get_parameters_by_path(
            Path=ssm_parameter_path,
            Recursive=False,
            WithDecryption=True
        )

        # Loop through the returned parameters and populate the ConfigParser
        if 'Parameters' in param_details and len(param_details.get('Parameters')) > 0:
            for param in param_details.get('Parameters'):
                param_path_array = param.get('Name').split("/")
                section_position = len(param_path_array) - 1
                section_name = param_path_array[section_position]
                config_values = json.loads(param.get('Value'))
                config_dict = {section_name: config_values}
                print("Found configuration: " + str(config_dict))
                configuration.read_dict(config_dict)

    except:
        print("Encountered an error loading config from SSM.")
        traceback.print_exc()
    finally:
        return configuration


def get_config():
    global myconfig
    # Initialize app if it doesn't yet exist
    if myconfig is None:
        print("Loading config and creating new MyConfig...")
        config = load_config(full_config_path)
        myconfig = MyConfig(config)

    print("MyConfig is " + str(myconfig.get_config()._sections))
    return myconfig


def get_app_config():
    global appconfig
    # Initialize app if it doesn't yet exist
    if appconfig is None:
        print("Loading app config and creating new AppConfig...")
        config = load_config(short_config_path)
        appconfig = MyConfig(config)

    print("AppConfig is " + str(appconfig.get_config()._sections))
    return appconfig
