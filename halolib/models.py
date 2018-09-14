from __future__ import print_function

import datetime
import logging

from django.conf import settings

# java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -port 8600
# java -D"java.library.path"=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -port 8600

logger = logging.getLogger(__name__)

ver = settings.DB_VER
uri = settings.DB_URL
tbl = False
page_size = settings.PAGE_SIZE


class AbsDbMixin(object):
    logprefix = None

    def __init__(self, logprefix):
        self.logprefix = logprefix

    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if hasattr(attr, '__call__'):
            def newfunc(*args, **kwargs):
                now = datetime.datetime.now()
                result = attr(*args, **kwargs)
                total = datetime.datetime.now() - now
                logger.info(self.logprefix + "timing for DBACCESS " + attr.__name__ + " in milliseconds : " + str(
                    int(total.total_seconds() * 1000)))
                return result

            return newfunc
        else:
            return attr
