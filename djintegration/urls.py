from django.conf.urls.defaults import *
from djintegration.settings import INT_DIR
from django.views.static import serve

urlpatterns = patterns('djintegration.views',
    url(r'^$', 'lastest_reports', name="latest-reports"),
    url(r'^repo/(?P<repo_id>[0-9]+)$', 'repository', name="repository"),
    url(r'^code/(?P<path>.*)$', serve,
        {'document_root': INT_DIR,  'show_indexes': True}, name='serve-integration-dir'),
)
