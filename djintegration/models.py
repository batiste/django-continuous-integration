"""Repositories ``models``."""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from datetime import datetime

REPOS = (
    ('git', 'Git'),
    ('svn', 'Subversion'),
    ('hg', 'Mercurial'),
)


class Repository(models.Model):
    """Represent a repository"""

    url = models.CharField(_('URL'), blank=False, max_length=250)
    type = models.CharField(_('Type'), choices=REPOS, max_length=10)
    last_commit = models.CharField(_('Last commit'), max_length=100,
        blank=True)
    creation_date = models.DateTimeField(_('creation date'), editable=False,
        default=datetime.now)

    def last_test_report(self):
        return TestReport.objects.filter(repository=self).latest('creation_date')
        

    class Meta:
        get_latest_by = 'creation_date'
        verbose_name = _('Repository')
        verbose_name_plural = _('Repositories')

    def __unicode__(self):
        return "%s" % (self.url)


class TestReport(models.Model):
    """Test report"""
    repository = models.ForeignKey(Repository)
    creation_date = models.DateTimeField(_('creation date'), editable=False,
        default=datetime.now)

    commit = models.CharField(_('Commit'), max_length=100, blank=False)
    result = models.TextField(blank=True)

    def fail(self):
        return (self.result.find('Error') != -1 or
            self.result.find('Failure') != -1)
    
    class Meta:
        verbose_name = _('Test report')
        verbose_name_plural = _('Test reports')
    
    def __unicode__(self):
        return "Test report %d (%s, %s)" % (self.pk,
            self.repository.url, self.commit)

