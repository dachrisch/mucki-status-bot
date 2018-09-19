# coding=utf-8
from unittest import TestCase

from remote_service.remotes import RemoteMethod, remote_methods_string


class TestRemotes(TestCase):
    def test_method_to_string(self):
        self.assertEqual('Google - Remote @ test', '%s' % str(RemoteMethod('Google', 'test')))

    def test_method_with_login_to_string(self):
        self.assertEqual('Google - Remote @ test\ncredentials: here',
                         '%s' % str(RemoteMethod('Google', 'test', 'here')))

    def test_google_in_methods(self):
        self.assertIn('---------------------\n'
                      'Google - Remote @ https://', remote_methods_string())

    def test_zoom_in_methods(self):
        self.assertIn('---------------------\n'
                      'Zoom - Remote @ https://zoom.us/', remote_methods_string())

    def test_talkyoo_in_methods(self):
        self.assertIn('---------------------\n'
                      'Talkyoo - Remote @ tel:+494095063183', remote_methods_string())
