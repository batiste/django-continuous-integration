============================================================================
djintegration - Continuous integration reports for python
============================================================================

Introduction
==============

Django continuous integration is a language agnostic tool for running and displaying
tests.

Although python and Django are used, this tools is can be used
with any project that have proper command line tests.

Django continuous integration currently support Git, Subversion and Mercurial. Creating
new backend for other source control tools is very simple.

What it doesn't do (yet)
=========================

This package has no support for virtualenv or installing the dependencies
of the applications you want to test. You have to manually make sure
that the application you are testing has the proper environnement to run
the tests.

This package is not a client/server architecture yet. All the tests are run
on the server.

How does it work
=================

You need to create a repository within the admin
and add a test command (the default being `"python setup.py test"`).

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


Get started
=============

Like all Django application you need to syncdb::

    $ cd testproj/
    $ python manage.py syncdb
    $ python manage.py runserver

Then go the administration interface and add your repositories.


.. image:: http://img708.imageshack.us/img708/7711/testsw.png
