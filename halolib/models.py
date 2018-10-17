from __future__ import print_function

import datetime
import logging

from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model

from halolib.logs import log_json
from .const import settingsx

# from django.conf import settings
settings = settingsx()

# java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -port 8600
# java -D"java.library.path"=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -port 8600

logger = logging.getLogger(__name__)

ver = settings.DB_VER
uri = settings.DB_URL
tbl = False
page_size = settings.PAGE_SIZE


class AbsDbMixin(object):
    # intercept db calls

    req_context = None

    def __init__(self, req_context):
        self.req_context = req_context

    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if hasattr(attr, '__call__'):
            def newfunc(*args, **kwargs):
                now = datetime.datetime.now()
                result = attr(*args, **kwargs)
                total = datetime.datetime.now() - now
                logger.info("performance_data", extra=log_json(self.req_context,
                                                               {"type": "DBACCESS",
                                                           "milliseconds": int(total.total_seconds() * 1000),
                                                           "function": str(attr.__name__)}))
                return result

            return newfunc
        else:
            return attr


class AbsModel(Model):
    halo_request_id = UnicodeAttribute(null=False)

    @classmethod
    def get_pre(cls):
        hash_key_name = super(AbsModel, cls)._hash_key_attribute().attr_name
        range_key_name = None
        attr = super(AbsModel, cls)._range_key_attribute()
        if attr:
            range_key_name = attr.attr_name
        print("\nhash_key_name=" + str(hash_key_name))
        print("\nrange_key_name=" + str(range_key_name))
        return hash_key_name, range_key_name

    def get_pre_val(self):
        hash_key_name, range_key_name = self.get_pre()
        hash_key_val = super(AbsModel, self).__getattribute__(hash_key_name)
        range_key_val = None
        if range_key_name:
            range_key_val = super(AbsModel, self).__getattribute__(range_key_name)
        print("\nhash_key_name=" + hash_key_name + "=" + str(hash_key_val))
        if range_key_val:
            print("\nrange_key_val=" + range_key_name + "=" + str(range_key_val))
        return hash_key_val, range_key_val

    def save(self, halo_request_id, condition=None, conditional_operator=None, **expected_values):
        if condition is None:
            condition = AbsModel.halo_request_id.does_not_exist()
        else:
            condition = condition & (AbsModel.halo_request_id.does_not_exist())
        hash_key_val, range_key_val = self.get_pre_val()
        request_id = halo_request_id + "-" + hash_key_val
        if range_key_val:
            request_id = request_id + "-" + range_key_val
        self.halo_request_id = request_id
        return super(AbsModel, self).save(condition, conditional_operator, **expected_values)
