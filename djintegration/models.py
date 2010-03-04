"""Repositories ``models``."""
from djintegration.settings import INT_DIR

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from datetime import datetime
import md5
import os

REPOS = (
    ('git', 'Git'),
    ('svn', 'Subversion'),
    ('hg', 'Mercurial'),
)


STATE = (
    ('fail', 'Fail'),
    ('pass', 'Pass'),
)

VIRTUAL_ENV = (
    ('vs', 'Virtualenv with Setuptools'),
    ('vd', 'Virtualenv with Distribute >= 1.4.4'),
    #('bs', 'Buildout with Setuptools'),
    #('bd', 'Buildout with Distribute'),
    ('no', 'No virtual environnement'),
)


class Repository(models.Model):
    """Represent a repository"""

    url = models.CharField(_('URL'), blank=False, max_length=250)
    type = models.CharField(_('Type'), choices=REPOS, max_length=10, default='git')
    last_commit = models.CharField(_('Last commit'), max_length=100,
        blank=True)
    creation_date = models.DateTimeField(_('creation date'), editable=False,
        default=datetime.now)

    virtual_env_type = models.CharField(_('Virtual environnement'),
        choices=VIRTUAL_ENV, max_length=16, default="vs")

    install_command = models.TextField(_('Install command'),
        blank=True,
        help_text='Default: "python setup.py install"')

    test_command = models.TextField(_('Test command'),
        blank=True,
        help_text='Default: "python setup.py test"')

    state = models.CharField(_('State'), choices=STATE, max_length=10, default='fail')

    emails = models.TextField(_('Notification emails'),
        blank=True,
        help_text='Default: settings.DJANGO_INTEGRATION_MAILS, comma separated.')

    def fail(self):
        return self.state == 'fail'

    def last_test_report(self):
        return TestReport.objects.filter(repository=self).latest('creation_date')

    def get_install_command(self):
        return self.install_command or 'python setup.py install'

    def get_test_command(self):
        return self.test_command or 'python setup.py test'

    def has_coverage(self):
        cov_dir = os.path.join(INT_DIR, self.dirname() + '-cov/')
        return os.path.exists(cov_dir)

    def dirname(self):
        m = md5.new()
        m.update(self.url)
        return m.hexdigest()

    def coverage_url(self):
        return self.dirname() + '-cov/index.html'

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

    install = models.TextField(blank=True)
    
    result = models.TextField(blank=True)
    
    author = models.CharField(_('Author'), max_length=100, blank=True)

    state = models.CharField(_('State'), choices=STATE, max_length=10)

    def fail(self):
        return self.state == 'fail'
    
    class Meta:
        verbose_name = _('Test report')
        verbose_name_plural = _('Test reports')
    
    def __unicode__(self):
        return "Test report %d (%s, %s)" % (self.pk,
            self.repository.url, self.commit)

