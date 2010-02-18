"""
Django continuous integration test suite.
"""
from djintegration.backends import GitBackend, SvnBackend, MercurialBackend

import unittest

class SourceControlTestCase(unittest.TestCase):
    """Django continuous integration test suite. class"""

    def test_backends(self):

        git = GitBackend('fake')
        log = open('djintegration/tests/gitlog.txt').read()
        self.assertEqual(git.get_commit(log),
            '0873bdde7f216304800fe1a22325cb60ee492f54')
        self.assertEqual(git.get_author(log),
            'Batiste Bieler <batisteb@opera.com>')

        svn = SvnBackend('fake')
        log = open('djintegration/tests/svninfo.txt').read()
        self.assertEqual(svn.get_commit(log), '466')
        self.assertEqual(svn.get_author(log), 'sehmaschine')

        svn = MercurialBackend('fake')
        log = open('djintegration/tests/hglog.txt').read()
        self.assertEqual(svn.get_commit(log), '164:7bc186caa7dc')
        self.assertEqual(svn.get_author(log), 'Tata Toto <toto@toto.com>')