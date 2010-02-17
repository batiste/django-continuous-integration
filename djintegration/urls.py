from django.conf.urls.defaults import *

urlpatterns = patterns('djintegration.views',
    url(r'^$', 'lastest_reports', name="latest-reports"),
)
