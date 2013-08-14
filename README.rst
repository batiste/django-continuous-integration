============================================================================
djintegration - Continuous integration reports for python
============================================================================

Introduction
==============

Django continuous integration is a tool for running and displaying
tests for the python language. Although python and Django are used,
this tools is meant to be used with any python project that has tests.

Django continuous integration currently support `Git`, `Subversion` and `Mercurial`.

.. image:: https://raw.github.com/batiste/django-continuous-integration/master/docs/shot.png


How does it work
=================

You need to create a repository within the admin by providing a repository URL
and add a test command (the default being `"python setup.py test"`).

For every test this software create a virtual python environnement (virtualenv)
and try to setup your python application by checking out your code and installing
the necesseray dependencies. It's nececessary that your package list all
the needed dependencies in `setup.py`. It's possible that you will have to
install some distribution dependencies by hand (like the developement headers for lxml).

Then you can generate a test report for all your repositories
using the `djintegration.commands.make_test_reports` commands
or by using the manage command::

    $ cd testproj/
    $ python manage.py maketestreports

This command will checkout your repositories in "/tmp/" and try to
execute the command you provided. The result will be stored in the
test report model.

The success or failure of the test is determined by the return code
of the test command.

Using buildout
===============

If you use builout with your project, you will not need any virtual environnement.
Choose "No virtual environnement" in the admin options.
Then you can execute your builout commands within the install textarea::

    python <your-project>/bootstrap.py --distribute
    ./bin/buildout -v

Coverage support
=================

If you support coverage in your tests, Django continuous will search for the coverage HTML directory.
The name of the directory has to be `covhtml` or `htmlcov`. You can override this setting::

    DJANGO_INTEGRATION_COV_CANDIDATES = ['htmlcov', 'covhtml', '...']

If found, the coverage HTML directory will be served via the web interface.


Settings
===========

DJANGO_INTEGRATION_MAILS
---------------------------

Default value: []

A list of emails where the failing tests are sent. You can override this value within the administration.

DJANGO_INTEGRATION_FROM_MAIL
------------------------------

Default value: "django-continuous-integration@noreply.com"

"From" field for report emails.

DJANGO_INTEGRATION_MAIL_TITLE
-------------------------------

Default value: "%s latest tests didn\'t passed"

"Title" field for report emails, `%s` is the repository `URL`.

DJANGO_INTEGRATION_DIRECTORY
--------------------------------

Default value: "/tmp/"

Directory where the virtualenv will be created and test runned.


What it doesn't do (yet)
=========================

This package is not a client/server architecture yet. All the tests are run
on the server.

Make it run automaticaly
==========================

As you could have multiple repositories in different locations, I think polling is a
realisitic approch. For that ou could use a cron job to make it run every 10 minutes::

    */10 *   *   *   *    cd /project/directory/;python manage.py maketestreports >> reports.log

Get started
=============

Like all Django application you need to syncdb::

    $ cd testproj/
    $ python manage.py syncdb
    $ python manage.py runserver

Then go the administration interface and add your repositories.


