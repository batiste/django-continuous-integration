
import os
import md5
import sys
import shlex
from subprocess import Popen, PIPE, STDOUT

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

def line_that_starts_with(log, start):
    for line in log.split('\n'):
        if line.startswith(start):
            return line.split(start)[1].strip()

class RepoBackend(object):

    checkout_cmd = None
    update_cmd = None

    def __init__(self, repo, *args, **kwargs):
        self.repo = repo

    def dirname(self):
        m = md5.new()
        m.update(self.repo.url)
        from django.conf import settings
        rdir = getattr(settings, 'DJ_INTEGRATION_DIRECTORY', '/tmp/')
        return rdir + m.hexdigest()

    def exist(self):
        def _exist():
            if os.path.exists(self.dirname()):
                return True
            return False
        from django.conf import settings
        rdir = getattr(settings, 'DJ_INTEGRATION_DIRECTORY', '/tmp/')
        return with_dir(rdir, _exist)

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
                author = self.last_commit_author()
                # this is only to keep unit tests working without
                # having to setup the django settings module
                from djintegration.models import TestReport
                test = TestReport(
                    repository=self.repo,
                    result=result,
                    commit=commit,
                    author=author
                )
                test.save()
                self.repo.save()
                return test
            return None
        return with_dir(self.dirname(), _update)


    def last_commit(self):
        def _commit():
            log = system(self.log_cmd)
            return self.get_commit(log)
        return with_dir(self.dirname(), _commit)

    def last_commit_author(self):
        def _commit():
            log = system(self.log_cmd)
            return self.get_author(log)
        return with_dir(self.dirname(), _commit)

class GitBackend(RepoBackend):

    checkout_cmd = 'git clone %s %s'
    update_cmd = 'git pull'
    log_cmd = 'git log -n 1'

    def get_commit(self, log):
        return line_that_starts_with(log, 'commit ')

    def get_author(self, log):
        return line_that_starts_with(log, 'Author: ')

class SvnBackend(RepoBackend):

    checkout_cmd = 'svn checkout %s %s'
    update_cmd = 'svn up'
    log_cmd = 'svn info'

    def get_commit(self, log):
        return line_that_starts_with(log, 'Revision: ')

    def get_author(self, log):
        return line_that_starts_with(log, 'Last Changed Author: ')


class MercurialBackend(RepoBackend):

    checkout_cmd = 'hg clone %s %s'
    update_cmd = 'hg pull'
    log_cmd = 'hg log --limit 1'

    def get_commit(self, log):
        return line_that_starts_with(log, 'changeset: ')

    def get_author(self, log):
        return line_that_starts_with(log, 'user: ')

