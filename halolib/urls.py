from __future__ import print_function

from django.conf.urls import *

from .views import *

urlpatterns = [
    #url(r'^upc/(?P<upc>\w+)/$', UpcLink.as_view(), name='upc'),
    #url(r'^task/(?P<upc>\w+)/$', TaskLink.as_view(), name='task'),
    url(r'^$', TestLink.as_view(), name='task'),
    url(r'^pref$', PrefLink.as_view(), name='pref'),
]

