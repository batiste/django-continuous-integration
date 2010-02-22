============================================================================
djintegration - Continuous integration reports for python
============================================================================

Introduction
==============

Django continuous integration is a tool for running and displaying
tests for the python language. Although python and Django are used,
this tools is meant to be used with any python project that has tests.

Django continuous integration currently support `Git`, `Subversion` and `Mercurial`.


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

The success or failure of the test is determined by the presence
of certain keywords within the the test result.


What it doesn't do (yet)
=========================

This package is not a client/server architecture yet. All the tests are run
on the server.

Get started
=============

Like all Django application you need to syncdb::

    $ cd testproj/
    $ python manage.py syncdb
    $ python manage.py runserver

Then go the administration interface and add your repositories.


.. image:: http://img708.imageshack.us/img708/7711/testsw.png
