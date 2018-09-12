from __future__ import print_function

import logging

from django.conf import settings

# java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -port 8600
# java -D"java.library.path"=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -port 8600

logger = logging.getLogger(__name__)

ver = settings.DB_VER
uri = settings.DB_URL
tbl = False
page_size = settings.PAGE_SIZE
