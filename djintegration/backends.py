
import re
import os
import sys
import shlex
import shutil
from subprocess import Popen, PIPE, STDOUT

from djintegration.models import TestReport
from djintegration.settings import INT_DIR, COV_CANDIDATES, TESTED_APP_DIR


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

def is_virtualenv_command(cmd):
    if (cmd.startswith('easy_install') or
        cmd.startswith('pip') or
        cmd.startswith('python')):
        return True
    else:
        return False

class RepoBackend(object):

    use_virtualenv = False
    checkout_cmd = None
    update_cmd = None

    def __init__(self, repo, *args, **kwargs):
        self.repo = repo

    def system(self, commands):
        commands = str(commands)
        
        args = shlex.split(commands)
        process = Popen(args, stdout=PIPE, stderr=STDOUT)
        output, errors = process.communicate()
        return output, process.returncode

    def dirname(self):
        return os.path.join(INT_DIR, self.repo.dirname() + '/')

    def app_dirname(self):
        return os.path.join(self.dirname(), TESTED_APP_DIR)

    def cov_dirname(self):
        return os.path.join(INT_DIR, self.repo.dirname() + '-cov/')

    def command_env(self, cmd):
        if is_virtualenv_command(cmd):
            cmd = 'bin/' + cmd
        def _command():
            return self.system(cmd)
        return with_dir(self.dirname(), _command)



    def command_app(self, cmd):
        if is_virtualenv_command(cmd):
            cmd = '../bin/' + cmd
        def _command():
            return self.system(cmd)
        return with_dir(self.dirname() + TESTED_APP_DIR, _command)

    def setup_env(self):
        # trash the old virtual env
        try:
            shutil.rmtree(self.dirname())
        except OSError:
            pass
        
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

        # it seems to be the only thing that work properly
        # ./bin/activate fails
        activate_this = self.dirname() + 'bin/activate_this.py'
        execfile(activate_this, dict(__file__=activate_this))
        
        return self.command_env(self.checkout_cmd %
            (self.repo.url, 'tested_app'))

    def run_tests(self):
        cmds = self.repo.get_test_command()
        cmds = cmds.replace('\r\n', ';')
        result = None
        for cmd in cmds.split(';'):
            result = self.command_app(cmd)
        return result

    def install(self):
        cmds = self.repo.get_install_command()
        cmds = cmds.replace('\r\n', ';')
        result = None
        for cmd in cmds.split(';'):
            result = self.command_app(cmd)
        return result

    def teardown_env(self):
        # search for coverage results directory
        cov_dir = None
        for directories in os.walk(self.app_dirname()):
            for candidate in COV_CANDIDATES:
                if candidate in directories[1]:
                    cov_dir = os.path.join(directories[0], candidate)
        if cov_dir:
            try:
                shutil.rmtree(self.cov_dirname())
            except OSError:
                pass
            shutil.move(cov_dir, self.cov_dirname())

    def make_report(self):
        
        self.setup_env()
        commit = self.last_commit()
        new_test = None
        
        if self.repo.last_commit != commit or len(commit) == 0 or True:
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

