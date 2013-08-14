import os, datetime
from celery.task import Task
from celery.registry import tasks
from djintegration.models import TestReport
from djintegration.commands import make_test_reports

fname = '/tmp/making_reports'



class MakeTestReportsTask(Task):

    def run(self, **kwargs):
        """
        Run this command unless it has been run recently.
        """
        numreports = TestReport.objects.count()
        make_test_reports()

class ForceTestReportsTask(Task):

    def run(self, **kwargs):
        """
        Run this command unless it has been run recently.
        """
        numreports = TestReport.objects.count()
        make_test_reports(force=True)

