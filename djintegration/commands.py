
from djintegration.models import Repository, TestReport
from djintegration.backends import get_backend
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

EMAILS = getattr(settings, 'DJANGO_INTEGRATION_MAILS', [])
FROM = getattr(settings, 'DJANGO_INTEGRATION_FROM_MAIL',
    'django-continuous-integration@noreply.com')
TITLE = getattr(settings, 'DJANGO_INTEGRATION_MAIL_TITLE',
    '%s latest tests didn\'t passed')


def make_test_reports(force=False):

    tests_to_report = []

    for repo in Repository.objects.all():
        print "Making test report for %s (%s)" % (repo.name, repo.url)
        backend = get_backend(repo)

        new_test = backend.make_report(force)
        if new_test and new_test.fail():
            tests_to_report.append(new_test)


    for test in tests_to_report:

        repo = test.repository

        if repo.emails:
            emails = repo.emails.split(',')
        else:
            emails = EMAILS

        title = TITLE % repo.url
        message = render_to_string('djintegration/error_email.html',
            {'test':test})

        send_mail(
            title,
            message,
            FROM,
            emails,
            fail_silently=True
        )
