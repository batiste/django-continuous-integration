
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

class GitBackend(RepoBackend):

    def create(self):
        if not self.exist():
            system('git clone %s %s' % (self.repo.url, self.dirname()))

    def update(self):
        def _update():
            system('git pull')
            commit = self.last_commit()
            #if self.repo.last_commit != commit:
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
        def _commit():
            log = system('git log -n 1')
            return log.split('\n')[0].split(' ')[1]
        return with_dir(self.dirname(), _commit)

def make_test_reports():

    for repo in Repository.objects.all():
        if repo.type == 'git':
            print "Making test report for %s" % repo.url
            backend = GitBackend(repo)
            backend.create()
            backend.update()
