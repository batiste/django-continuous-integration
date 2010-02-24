from django.conf.urls.defaults import *

urlpatterns = patterns('djintegration.views',
    url(r'^$', 'lastest_reports', name="latest-reports"),
    url(r'^repo/(?P<repo_id>[0-9]+)$', 'repository', name="repository"),
)
