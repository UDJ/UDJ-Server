from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^udj/0_6/', include('udj.urls06')),
    url(r'^udj/0_7/', include('udj.urls07')),
    url(r'^admin/', include(admin.site.urls)),


)


try:
  from urls_local import *
except ImportError:
  pass
