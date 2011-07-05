from django.conf.urls.defaults import *
from djintegration.settings import INT_DIR
from django.views.static import serve

urlpatterns = patterns('djintegration.views',
    url(r'^$', 'latest_reports', name="latest-reports"),
    url(r'^repo/(?P<repo_id>[0-9]+)$', 'repository', name="repository"),
    url(r'^code/(?P<path>.*)$', serve,
        {'document_root': INT_DIR,  'show_indexes': True}, name='serve-integration-dir'),
    url(r'^make$', 'make_reports', name="make-reports"),
    url(r'^force$', 'force_reports', name="force-reports"),
)
