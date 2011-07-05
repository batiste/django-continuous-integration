import os, datetime
from celery.task import Task
from celery.registry import tasks
from djintegration.models import TestReport
from djintegration.commands import make_test_reports

fname = '/tmp/making_reports'

def touch():
    times = None
    with file(fname, 'a'):
        os.utime(fname, times)

def is_recent():
    if os.path.exists(fname):
        t = os.path.getmtime( fname )
        fdt = datetime.datetime.fromtimestamp(t)
        now = datetime.datetime.now()
        dt = now - fdt
        print "seconds:", dt.seconds
        if dt.seconds < 360:
            return True
    return False

class MakeTestReportsTask(Task):

    def run(self, **kwargs):
        """
        Run this command unless it has been run recently.
        """
        if is_recent():
            pass
        else:
            numreports = TestReport.objects.count()
            make_test_reports()
            newnumreports = TestReport.objects.count()
            if newnumreports > numreports:
                touch()

class ForceTestReportsTask(Task):

    def run(self, **kwargs):
        """
        Run this command unless it has been run recently.
        """
        if is_recent():
            pass
        else:
            numreports = TestReport.objects.count()
            make_test_reports(force=True)
            newnumreports = TestReport.objects.count()
            if newnumreports > numreports:
                touch()

