from django.conf.urls import *
from django.views.static import serve
from django.conf import settings

from views import *

urlpatterns = [
    #url(r'^upc/(?P<upc>\w+)/$', UpcLink.as_view(), name='upc'),
    #url(r'^task/(?P<upc>\w+)/$', TaskLink.as_view(), name='task'),
]


