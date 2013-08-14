from django.conf.urls.defaults import *
from djintegration.settings import INT_DIR
from django.views.static import serve

urlpatterns = patterns('djintegration.views',
    url(r'^$', 'latest_reports', name="latest-reports"),
    url(r'^repo/(?P<repo_id>[0-9]+)$', 'repository', name="repository"),
    url(r'^repopart/(?P<repo_id>[0-9]+)$', 'repository_partial', name="repository-partial"),
    url(r'^code/(?P<path>.*)$', serve,
        {'document_root': INT_DIR,  'show_indexes': True}, name='serve-integration-dir'),
    url(r'^makeall$', 'make_reports', name="make-reports"),
    url(r'^forceall$', 'force_reports', name="force-reports"),
    url(r'^make/(?P<repo_id>[0-9]+)$', 'make_report', name="make-report"),
    url(r'^taskstatus/(?P<task_id>[0-9a-zA-Z\-]+)$', 'task_status', name="task-status"),
)
