from django.db import models

#java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -port 8600

import uuid
import logging
from django.conf import settings
import datetime

from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ver = settings.DB_VER
uri = settings.DB_URL
tbl = False
page_size = settings.PAGE_SIZE
