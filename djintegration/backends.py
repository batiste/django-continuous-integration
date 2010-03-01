
import re
import os
import md5
import sys
import shlex
import shutil
from subprocess import Popen, PIPE, STDOUT

# To keep tests running
try:
    from django.conf import settings
    from djintegration.models import TestReport
    INT_DIR = getattr(settings, 'DJANGO_INTEGRATION_DIRECTORY', '/tmp/')
except ImportError:
    INT_DIR = '/tmp/'
    TestReport = None

TESTED_APP_DIR = 'tested_app/'


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

    use_virtualenv = False
    checkout_cmd = None
    update_cmd = None

    def __init__(self, repo, *args, **kwargs):
        self.repo = repo

    def system(self, commands, activate=False):
        commands = str(commands)
        if self.use_virtualenv:
            commands = '. ' + self.dirname() + 'bin/activate;' + commands
        commands = commands.replace('\r\n', ';')
        args = shlex.split(commands)
        process = Popen(commands, shell=True, stdout=PIPE, stderr=STDOUT)
        returncode = process.returncode
        output, errors = process.communicate()
        return output, returncode

    def dirname(self):
        m = md5.new()
        m.update(self.repo.url)
        return INT_DIR + m.hexdigest() + '/'

    def exist(self):
        def _exist():
            if os.path.exists(self.dirname()):
                return True
            return False
        from django.conf import settings
        return with_dir(INT_DIR, _exist)

    def command_env(self, cmd):
        def _command():
            return self.system(cmd)
        return with_dir(self.dirname(), _command)

    def command_app(self, cmd):
        def _command():
            return self.system(cmd, True)
        return with_dir(self.dirname() + TESTED_APP_DIR, _command)

    def setup_env(self):
        virtual_env_commands = {
            'vs':'virtualenv --no-site-packages %s',
            'vd':'virtualenv --no-site-packages %s --distribute'
        }
        cmd = virtual_env_commands.get(self.repo.virtual_env_type, None)
        if cmd:
            self.system(cmd % self.dirname())
            self.use_virtualenv = True
        else:
            if not os.path.isdir(self.dirname()):
                os.makedirs(self.dirname())
        return self.command_env(self.checkout_cmd %
            (self.repo.url, 'tested_app'))

    def run_tests(self):
        cmd = self.repo.get_test_command()
        return self.command_app(cmd)

    def install(self):
        cmd = self.repo.get_install_command()
        return self.command_app(cmd)

    def teardown_env(self):
        shutil.rmtree(self.dirname())

    def make_report(self):
        
        self.setup_env()
        commit = self.last_commit()
        new_test = None
        
        if self.repo.last_commit != commit or len(commit) == 0:
            self.repo.last_commit = commit

            install_result, returncode1 = self.install()
            
            test_result, returncode2 = self.run_tests()
            author = self.last_commit_author()

            result_state = 'pass' if returncode2 == 0 else 'fail'
            new_test = TestReport(
                repository=self.repo,
                install=install_result,
                result=test_result,
                commit=commit,
                author=author,
                state=result_state,
            )
            new_test.save()
            self.repo.state = result_state
            self.repo.save()
        
        self.teardown_env()
        return new_test


    def last_commit(self):
        log, returncode = self.command_app(self.log_cmd)
        return self.get_commit(log)

    def last_commit_author(self):
        log, returncode = self.command_app(self.log_cmd)
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

