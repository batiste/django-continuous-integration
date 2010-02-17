# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from django.conf import settings
from djintegration.commands import make_test_reports

class Command(NoArgsCommand):
    """Generate the test reports from the latest commits."""

    help = "Generate the test reports from the latest commits."

    def handle_noargs(self, **options):
        make_test_reports()
