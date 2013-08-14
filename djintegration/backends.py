
import re
import os
import sys
import shlex
import shutil
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime, timedelta

from djintegration.models import TestReport, Repository
from djintegration.settings import INT_DIR, COV_CANDIDATES, TESTED_APP_DIR
from djintegration.settings import MAX_RUNNING_TIME

MAX_RUN_DELTA = timedelta(seconds=MAX_RUNNING_TIME)


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
        print "commands:", commands

        if ";" in commands:
            ret = os.system(commands)
            return "", ret
        else:
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



    def command_app(self, cmd, use_test_subpath=False):
        if is_virtualenv_command(cmd):
            cmd = '../bin/' + cmd
        def _command():
            return self.system(cmd)
        command_dir = self.dirname() + TESTED_APP_DIR
        if use_test_subpath:
            command_dir += '/' + self.repo.test_subpath
        return with_dir(command_dir, _command)

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
        cmds = cmds.replace('\r\n', ';;')
        result = None
        for cmd in cmds.split(';;'):
            if len(cmd):
                result = self.command_app(cmd, use_test_subpath=True)
        return result

    def install(self):
        cmds = self.repo.get_install_command()
        cmds = cmds.replace('\r\n', ';;')
        result = None
        for cmd in cmds.split(';;'):
            if len(cmd):
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

    def make_report(self, force=False):
      
        report = self.repo.last_test_report()
        if report:
            delta = datetime.now() - report.creation_date
            if report.state == "running" and delta < MAX_RUN_DELTA:
                print "Last report is still running, running time is %s" % str(delta)
                return report
    
        self.setup_env()
        commit = self.last_commit()
        new_test = None

        if force or self.repo.last_commit != commit or len(commit) == 0:

            author = self.last_commit_author()

            new_test = TestReport(
                repository=self.repo,
                install="Running ...",
                result="Running ...",
                commit=commit,
                author=author,
                state='running',
            )
            new_test.save()
            
            try:
                install_result, returncodeinstall = self.install()
                # mysql text field has a limitation on how large a text field can be
                # 65,535 bytes ~64kb
                mysql_text_limit = 40000
                install_result = install_result[-mysql_text_limit:]

                test_result, returncode = self.run_tests()
                test_result = test_result[-mysql_text_limit:]

            except e:
                returncode = 1
                install_result = str(e)
                test_result = str(e)

            if returncode == 0:
                result_state = "pass"
            else:
                result_state = "fail"
            new_test.install=install_result
            new_test.result=test_result    
            new_test.state=result_state,
            new_test.save()

            # this to avoid to override things that could have been modified in
            # the admin, we fetch the repo again.
            save_repo = Repository.objects.get(pk=self.repo.pk)
            save_repo.state = result_state
            save_repo.last_commit = commit
            save_repo.save()

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

