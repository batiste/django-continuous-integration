============================================================================
djintegration - Continuous integration reports for python
============================================================================

Introduction
============

Django continuous integration is a language agnostic tool for running and displaying
tests.

Although python and Django are used, this tools is intenteded to be used
with any project that have proper command line tests.

Django continuous integration currently support Git, Subversion and Mercurial. Creating
new backend for other source control tools is very simple.

What it doesn't do (yet)
========================

This package has no support for virtualenv or installing the dependencies
of the applications you want to test. You have to manually make sure
that the application you are testing has the proper environnement to run
the tests.

Get started
============

Like all Django application you need to syncdb::

    $ cd testproj/
    $ python manage.py syncdb
    $ python manage.py runserver

Then go the administration interface and add your repositories.

Register repositories to be part of the continuous integration
==================================================================

To generate a test report execute `djintegration.commands.make_test_reports` by using the manage command::

    $ cd testproj/
    $ python manage.py maketestreports


.. image:: http://img708.imageshack.us/img708/7711/testsw.png
