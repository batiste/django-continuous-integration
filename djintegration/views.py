from djintegration.models import Repository, TestReport

from django.shortcuts import render_to_response
from django.template import RequestContext

def lastest_reports(request):

    repos = list(Repository.objects.filter(state='fail')) + \
        list(Repository.objects.filter(state='pass'))
    
    return render_to_response('djintegration/latest_reports.html',
        RequestContext(request, locals()))

def repository(request, repo_id):

    repo = Repository.objects.get(pk=int(repo_id))
    tests = TestReport.objects.filter(repository=repo).order_by('-creation_date')[0:30]

    return render_to_response('djintegration/repository.html',
        RequestContext(request, locals()))