# coding=UTF-8
import re
import unittest

from telegram import Update
from telegram.ext import RegexHandler

from yammer_service.highlights import Highlights, HIGHLIGHTS_PATTERN

HASH_AND_COLON = '#highlights: test'

BOTH_HASH = '#highlights test #highlights'

BACK_HASH = 'test #highlights'

FRONT_HASH = '#highlights test'


class _Any(object):
    pass


class TestHighlights(unittest.TestCase):
    def test_regex_both(self):
        match = re.match(HIGHLIGHTS_PATTERN, BOTH_HASH)
        self.assertTrue(bool(match))

    def test_regex_front(self):
        match = re.match(HIGHLIGHTS_PATTERN, FRONT_HASH)
        self.assertTrue(bool(match))

    def test_regex_back(self):
        match = re.match(HIGHLIGHTS_PATTERN, BACK_HASH)
        self.assertTrue(bool(match))

    def test_regex_hash_colon(self):
        match = re.match(HIGHLIGHTS_PATTERN, HASH_AND_COLON)
        self.assertTrue(bool(match))

    def test_simple_text(self):
        highlights = Highlights()
        self.assertFalse(highlights.add('Chris', 'test'))

    def test_hash_front(self):
        highlights = Highlights()
        self.assertTrue(highlights.add('Chris', FRONT_HASH))
        self.assertEqual('test', highlights.get('Chris'))

    def test_hash_back(self):
        highlights = Highlights()
        self.assertTrue(highlights.add('Chris', BACK_HASH))
        self.assertEqual('test', highlights.get('Chris'))

    def test_hash_multiple(self):
        highlights = Highlights()
        self.assertTrue(highlights.add('Chris', BOTH_HASH))
        self.assertEqual('test', highlights.get('Chris'))

    def test_hash_and_colon(self):
        highlights = Highlights()
        self.assertTrue(highlights.add('Chris', HASH_AND_COLON))
        self.assertEqual('test', highlights.get('Chris'))

    def test_handler_regex_front(self):
        rh = RegexHandler(HIGHLIGHTS_PATTERN, None)
        message = _Any()
        message.text = '#highlights test'
        self.assertTrue(rh.check_update(Update(1234, message=message)))

    def test_handler_regex_back(self):
        rh = RegexHandler(HIGHLIGHTS_PATTERN, None)
        message = _Any()
        message.text = 'test #highlights'
        self.assertTrue(rh.check_update(Update(1234, message=message)))


if __name__ == '__main__':
    unittest.main()
