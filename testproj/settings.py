# Django settings for test_proj project.
import os
PROJECT_DIR = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('somebody', 'somebody@gmail.com'),
)

DJANGO_INTEGRATION_DIRECTORY = '/tmp/dci'

MANAGERS = ADMINS

# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dci.db'
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

STATIC_URL = "/static/"

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'kwjdckjwdcl0@ku!3&wi4kx4$yqnwctw*cf2kmi(0p=#3n!jl!0kp!o18wn^'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
    #'testproj.middleware.RestrictMiddleware',
)

ROOT_URLCONF = 'testproj.urls'

DJANGO_INTEGRATION_MAILS = ['batisteb@opera.com']

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'djcelery',
    'djintegration',
)

# commit hook callback settings
# Your commit hook must send a POST request to /make
# Some value in the post REQUEST must include the REQUIRED_CALLBACK_STRING as well
#   as one of the CONFRIM_CALLBACK_STRINGS. (The IP address of the callback sender
#   does not need to be in the IP_WHITELIST.)
# To change this behaviour, reqork the middleware.py file.
# This stuff was tested with unfuddle.com.

# IP_WHITELIST = ['127.0.0.1']
# REQUIRED_CALLBACK_STRING = 'repository'
# CONFIRM_CALLBACK_STRINGS = ['mycompany.com']

# celery settings

import djcelery
djcelery.setup_loader()

BROKER_BACKEND  = 'djkombu.transport.DatabaseTransport'
BROKER_HOST     = 'localhost'
BROKER_PORT     = 5672
BROKER_USER     = 'someuser'
BROKER_PASSWORD = 'somepass'
BROKER_VHOST    = '/'

