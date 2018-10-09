from __future__ import print_function

import datetime
import logging

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
