import os, datetime
from celery.task import Task
from celery.registry import tasks
from djintegration.models import TestReport
from djintegration.commands import make_test_reports
from djintegration.backends import get_backend

fname = '/tmp/making_reports'



class MakeTestReportsTask(Task):

    def run(self, **kwargs):
        numreports = TestReport.objects.count()
        make_test_reports()

class ForceTestReportsTask(Task):

    def run(self, **kwargs):
        numreports = TestReport.objects.count()
        make_test_reports(force=True)
        
class MakeTestReportTask(Task):

    def run(self, repository, force, **kwargs):

        backend = get_backend(repository)
        backend.make_report(force)
        