============================================================================
djintegration - Continuous integration reports for python
============================================================================

:Version: 0.0.1

Introduction
============

Django continuous integration is a tool for running and displaying
tests for projects.

Although Django is used, this tools is intenteded to be used
with any python project that have proper tests.

Django continuous integration currently support Git and Subversion and Mercurial. Creating
new backend for other tools is very simple.

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
