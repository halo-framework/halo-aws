from django.conf.urls import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Example:
    url(r'^', include('common.commonapi.urls')),
    #url(r'^', proxy),
    #url(r'^(?P<url>.*)$', proxy),#, ProxyLink.as_view(), name='proxy'),

    #url(r'^common/', include('common.commonapi.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),

    #url(r'^api-token-auth/', include('rest_framework.authtoken.views.obtain_auth_token')),
] #+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


