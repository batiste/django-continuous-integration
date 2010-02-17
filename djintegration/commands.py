
from djintegration.models import Repository, TestReport

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

class RepoBackend(object):

    checkout_cmd = None
    update_cmd = None

    def __init__(self, repo, *args, **kwargs):
        self.repo = repo

    def dirname(self):
        m = md5.new()
        m.update(self.repo.url)
        return '/tmp/' + m.hexdigest()

    def exist(self):
        def _exist():
            if os.path.exists(self.dirname()):
                return True
            return False
        return with_dir('/tmp/', _exist)

    def create(self):
        if not self.exist():
            system(self.checkout_cmd % (self.repo.url, self.dirname()))

    def update(self):
        def _update():
            system(self.update_cmd)
            commit = self.last_commit()
            if self.repo.last_commit != commit or len(commit) == 0:
                self.repo.last_commit = commit
                result = system('python setup.py test')
                test = TestReport(
                    repository=self.repo,
                    result=result,
                    commit=commit
                )
                test.save()
                self.repo.save()
        with_dir(self.dirname(), _update)

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

def make_test_reports():

    for repo in Repository.objects.all():
        if repo.type == 'git':
            print "Making test report for %s" % repo.url
            backend = GitBackend(repo)
            backend.create()
            backend.update()
        if repo.type == 'svn':
            print "Making test report for %s" % repo.url
            backend = SvnBackend(repo)
            backend.create()
            backend.update()
