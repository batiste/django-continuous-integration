import sys
from djintegration.models import Repository, TestReport
from djintegration.tasks import MakeTestReportsTask
from djintegration.tasks import ForceTestReportsTask, MakeTestReportTask
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django import http
from celery.result import AsyncResult

def latest_reports(request):

    repos = list(Repository.objects.filter(state='fail')) + \
        list(Repository.objects.filter(state='pass'))
    
    return render_to_response('djintegration/latest_reports.html',
        RequestContext(request, locals()))
        
def repository(request, repo_id):

    repo = Repository.objects.get(pk=int(repo_id))
    tests = TestReport.objects.filter(repository=repo).order_by('-creation_date')[0:30]

    return render_to_response('djintegration/repository.html',
        RequestContext(request, locals()))
        
def repository_partial(request, repo_id):
    repo = Repository.objects.get(pk=int(repo_id))
    return render_to_response('djintegration/repository_partial.html',
        RequestContext(request, {"repo":repo}))

def make_reports(request):
    if not request.user.is_staff:
        http.HttpResponse("Not allowed")
        
    MakeTestReportsTask.delay()
    response = latest_reports(request)   
    return redirect('/')

def force_reports(request):
    if not request.user.is_staff:
        http.HttpResponse("Not allowed")
        
    ForceTestReportsTask.delay()
    response = latest_reports(request)
    return redirect('/')

def make_report(request, repo_id):
  
    force = request.GET.get("force") == "true"
  
    if not request.user.is_staff:
        http.HttpResponse("Not allowed")

    repo = Repository.objects.get(pk=int(repo_id))
    task = MakeTestReportTask()
    result = task.delay(repo, force)
    
    return http.HttpResponse(result.id)
    
def task_status(request, task_id):

    res = AsyncResult(task_id)
    return http.HttpResponse(str(res.ready()))
    