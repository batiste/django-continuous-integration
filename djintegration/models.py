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


STATE = (
    ('fail', 'Fail'),
    ('pass', 'Pass'),
)


class Repository(models.Model):
    """Represent a repository"""

    url = models.CharField(_('URL'), blank=False, max_length=250)
    type = models.CharField(_('Type'), choices=REPOS, max_length=10)
    last_commit = models.CharField(_('Last commit'), max_length=100,
        blank=True)
    creation_date = models.DateTimeField(_('creation date'), editable=False,
        default=datetime.now)

    test_command = models.TextField(_('Test command'),
        blank=True,
        help_text='Default: "python setup.py test"')

    state = models.CharField(_('State'), choices=STATE, max_length=10)

    def fail(self):
        return self.state == 'fail'

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
    install = models.TextField(blank=True)
    author = models.CharField(_('Author'), max_length=100, blank=True)

    state = models.CharField(_('State'), choices=STATE, max_length=10)

    def fail(self):
        result = self.result.lower()
        def contains(text):
            return result.find(text) != -1

        if contains('0 error') and contains('0 failure'):
            return False

        if contains('error') or contains('failure'):
            return True

        return False
    
    class Meta:
        verbose_name = _('Test report')
        verbose_name_plural = _('Test reports')
    
    def __unicode__(self):
        return "Test report %d (%s, %s)" % (self.pk,
            self.repository.url, self.commit)

