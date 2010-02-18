
from djintegration.models import Repository, TestReport
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

import os
import md5
import sys
import shlex
from subprocess import Popen, PIPE, STDOUT

REPOS_DIR = getattr(settings, 'DJ_INTEGRATION_DIRECTORY', '/tmp/')
EMAILS = getattr(settings, 'DJANGO_INTEGRATION_MAILS', [])

def system(command_line):
    command_line = str(command_line)
    args = shlex.split(command_line)
    p = Popen(args, stdout=PIPE, stderr=STDOUT)
    output, errors = p.communicate()
    return output

def with_dir(dirname, fun):
    cwd = os.getcwd()
    result = None
    try:
        os.chdir(dirname)
        result = fun()
    finally:
        os.chdir(cwd)
    return result

class RepoBackend(object):

    checkout_cmd = None
    update_cmd = None

    def __init__(self, repo, *args, **kwargs):
        self.repo = repo

    def dirname(self):
        m = md5.new()
        m.update(self.repo.url)
        return REPOS_DIR + m.hexdigest()

    def exist(self):
        def _exist():
            if os.path.exists(self.dirname()):
                return True
            return False
        return with_dir(REPOS_DIR, _exist)

    def create(self):
        if not self.exist():
            system(self.checkout_cmd % (self.repo.url, self.dirname()))

    def update(self):
        def _update():
            system(self.update_cmd)
            commit = self.last_commit()
            if self.repo.last_commit != commit or len(commit) == 0:
                self.repo.last_commit = commit
                test_command = self.repo.test_command or 'python setup.py test'
                result = system(test_command)
                test = TestReport(
                    repository=self.repo,
                    result=result,
                    commit=commit
                )
                test.save()
                self.repo.save()
                return test
            return None
        return with_dir(self.dirname(), _update)
            

    def last_commit(self):
        raise NotImplemented

class GitBackend(RepoBackend):

    checkout_cmd = 'git clone %s %s'
    update_cmd = 'git pull'

    def last_commit(self):
        def _commit():
            log = system('git log -n 1')
            return log.split('\n')[0].split(' ')[1]
        return with_dir(self.dirname(), _commit)

class SvnBackend(RepoBackend):

    checkout_cmd = 'svn checkout %s %s'
    update_cmd = 'svn up'

    def last_commit(self):
        def _commit():
            log = system('svn info')
            return log.split('\n')[4].split(' ')[1]
        return with_dir(self.dirname(), _commit)

class MercurialBackend(RepoBackend):

    checkout_cmd = 'hg clone %s %s'
    update_cmd = 'hg pull'

    def last_commit(self):
        def _commit():
            log = system('hg log --limit 1')
            return log.split('\n')[0].split(' ')[-1]
        return with_dir(self.dirname(), _commit)

def make_test_reports():

    tests_to_report = []

    for repo in Repository.objects.all():
        print "Making test report for %s" % repo.url
        if repo.type == 'git':
            backend = GitBackend(repo)
        elif repo.type == 'svn':
            backend = SvnBackend(repo)
        elif repo.type == 'hg':
            backend = MercurialBackend(repo)

        backend.create()
        new_test = backend.update()
        if new_test and new_test.fail():
            tests_to_report.append(new_test)


    if tests_to_report:
        title = 'Continuous integration: some tests didn\'t passed'
        message = render_to_string('djintegration/error_email.html',
            {'tests':tests_to_report})
        send_mail(
            title,
            message,
            'noreply@example.com',
            EMAILS,
            fail_silently=False
        )