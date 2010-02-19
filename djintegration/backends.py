
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
        return rdir + m.hexdigest() + '/'

    def exist(self):
        def _exist():
            if os.path.exists(self.dirname()):
                return True
            return False
        from django.conf import settings
        rdir = getattr(settings, 'DJ_INTEGRATION_DIRECTORY', '/tmp/')
        return with_dir(rdir, _exist)

    def command_virtualenv(self, cmd):
        def _command():
            return system(cmd)
        return with_dir(self.dirname(), _command)

    def command_app(self, cmd):
        def _command():
            return system(cmd)
        return with_dir(self.dirname() + 'tested_app/', _command)

    def activate(self):
        activate_this = self.dirname() + 'bin/activate_this.py'
        execfile(activate_this, dict(__file__=activate_this))

    def setup_env(self):
        system('virtualenv --no-site-packages %s' % self.dirname())
        self.activate()
        self.command_virtualenv(self.checkout_cmd % (self.repo.url, 'tested_app'))

    def install_dependencies(self):
        self.command_app('python setup.py install')

    def teardown_env(self):
        system('rm -Rf %s' % self.dirname())

    def test_command(self):
        return self.repo.test_command or 'python setup.py test'

    def make_report(self):
        
        self.setup_env()
        commit = self.last_commit()
        new_test = None
        
        if self.repo.last_commit != commit or len(commit) == 0:
            self.repo.last_commit = commit

            self.install_dependencies()
            
            result = self.command_app(self.test_command())
            author = self.last_commit_author()

            # this is only to keep unit tests working without
            # having to setup the django settings module
            from djintegration.models import TestReport
            new_test = TestReport(
                repository=self.repo,
                result=result,
                commit=commit,
                author=author
            )
            test.save()
            self.repo.save()
        
        self.teardown_env()
        return new_test


    def last_commit(self):
        log = self.command_app(self.log_cmd)
        return self.get_commit(log)

    def last_commit_author(self):
        log = self.command_app(self.log_cmd)
        return self.get_author(log)

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

