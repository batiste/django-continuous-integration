
from djintegration.models import Repository, TestReport
from djintegration.backends import GitBackend, SvnBackend, MercurialBackend
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

EMAILS = getattr(settings, 'DJANGO_INTEGRATION_MAILS', [])

def make_test_reports():

    tests_to_report = []

    for repo in Repository.objects.all():
        print "Making test report for %s" % repo.url
        if repo.type == 'git':
            backend = GitBackend(repo)
        elif repo.type == 'svn':
            backend = SvnBackend(repo)
        elif repo.type == 'hg':
            backend = MercurialBackend(repo)

        new_test = backend.make_report()
        if new_test and new_test.fail():
            tests_to_report.append(new_test)


    if tests_to_report:
        title = 'Continuous integration: some tests didn\'t passed'
        message = render_to_string('djintegration/error_email.html',
            {'tests':tests_to_report})
        send_mail(
            title,
            message,
            'noreply@example.com',
            EMAILS,
            fail_silently=False
        )