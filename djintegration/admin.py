# -*- coding: utf-8 -*-
from os.path import join

from django.contrib import admin
from django.db import models
from django.conf import settings

from djintegration.models import Repository, TestReport

admin.site.register(TestReport)
admin.site.register(Repository)
