# coding=UTF-8
import re
import unittest
from abc import ABC

from telegram import Update
from telegram.ext import RegexHandler

from service.action import ActionMixin
from tests.telegram_test_bot import FailureThrowingRegexActionHandler, TelegramBotTest
from yammer_service.highlights import Highlights, HIGHLIGHTS_PATTERN, ShowHighlightsCommandAction, \
    HighlightsCollectorRegexAction

HASH_AND_COLON = '#highlights: test'

BOTH_HASH = '#highlights test #highlights'

BACK_HASH = 'test #highlights'

FRONT_HASH = '#highlights test'


class _Any(object):
    pass


class TestHighlightsMatching(unittest.TestCase):
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


class ConversationActionMixin(ActionMixin, ABC):
    pass


class TestShowHighlightsCommand(TelegramBotTest):
    def test_can_execute_show_highlights(self):
        highlights = Highlights()
        highlights.add('A', '#highlights test')
        self.assert_command_action_responses_with(ShowHighlightsCommandAction(highlights),
                                                  'the following')

    def test_show_highlights_is_empty(self):
        highlights = Highlights()
        self.assert_command_action_responses_with(ShowHighlightsCommandAction(highlights),
                                                  'no highlights')

    def test_collect_highlights(self):
        highlights = Highlights()

        handler = self.registry.register_action(HighlightsCollectorRegexAction(highlights),
                                                FailureThrowingRegexActionHandler)

        self.updater.dispatcher.process_update(self._create_update_with_text('#highlights test', 'A'))

        self._check_handler(handler)

        self.assertIn('A: test', highlights.message_string)

    def test_collect_highlights_responds(self):
        self.assert_regex_action_responses_with(HighlightsCollectorRegexAction(Highlights()),
                                                'collecting highlight for test')
