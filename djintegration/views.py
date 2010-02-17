from djintegration.models import Repository, TestReport

from django.shortcuts import render_to_response
from django.template import RequestContext

def lastest_reports(request):

    repos = Repository.objects.all()
    
    return render_to_response('djintegration/latest_reports.html',
        RequestContext(request, locals()))