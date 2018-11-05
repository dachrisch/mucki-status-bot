# coding=UTF-8
import re
import unittest

from telegram import Update
from telegram.ext import RegexHandler

from tests.telegram_test_bot import FailureThrowingRegexActionHandler, TelegramBotTest, \
    FailureThrowingConversationActionHandler
from yammer_service.highlights import Highlights, HIGHLIGHTS_PATTERN, ShowHighlightsCommandAction, \
    HighlightsCollectorRegexAction, SendHighlightsConversationAction, current_calendar_week
from yammer_service.yammer import YammerConnector

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
        self.assertFalse(highlights.add_pattern('Chris', 'test'))

    def test_hash_front(self):
        highlights = Highlights()
        self.assertTrue(highlights.add_pattern('Chris', FRONT_HASH))
        self.assertEqual('test', highlights.get('Chris'))

    def test_hash_back(self):
        highlights = Highlights()
        self.assertTrue(highlights.add_pattern('Chris', BACK_HASH))
        self.assertEqual('test', highlights.get('Chris'))

    def test_hash_multiple(self):
        highlights = Highlights()
        self.assertTrue(highlights.add_pattern('Chris', BOTH_HASH))
        self.assertEqual('test', highlights.get('Chris'))

    def test_hash_and_colon(self):
        highlights = Highlights()
        self.assertTrue(highlights.add_pattern('Chris', HASH_AND_COLON))
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


class TestShowHighlightsCommand(TelegramBotTest):
    def test_can_execute_show_highlights(self):
        highlights = Highlights()
        highlights.add_pattern('A', '#highlights test')
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


class YammerTestConnector(YammerConnector):
    def __init__(self):
        self.called = False

    def post_meine_woche(self, message, tags=()):
        self.called = True
        return message


class TestSendHighlights(TelegramBotTest):
    def test_empty_highlights_no_send(self):
        highlights = Highlights()

        self.registry.register_action(SendHighlightsConversationAction(highlights),
                                      FailureThrowingConversationActionHandler)

        self.updater.dispatcher.process_update(self._create_update_with_text('/send_highlights'))

        self.assertEqual('no highlights available', self.registry.writer_factory.writer.message)

    def test_ask_for_consent_before_sending(self):
        highlights = Highlights()
        highlights.add_pattern('A', '#highlights 1')

        assert len(highlights.highlights) == 1, highlights.highlights
        self.registry.register_action(SendHighlightsConversationAction(highlights),
                                      FailureThrowingConversationActionHandler)

        self.updater.dispatcher.process_update(self._create_update_with_text('/send_highlights'))

        self.assertEqual('the following highlights are available:\n'
                         'A: 1\n'
                         'really send?\n', self.registry.writer_factory.writer.message)

    def test_send_highlights_with_yes(self):
        highlights = Highlights()
        highlights.yc = YammerTestConnector()
        highlights.add_pattern('A', '#highlights 1')

        assert len(highlights.highlights) == 1, highlights.highlights
        self.registry.register_action(SendHighlightsConversationAction(highlights),
                                      FailureThrowingConversationActionHandler)

        ask_consent_update = self._create_update_with_text('/send_highlights')

        self.updater.dispatcher.process_update(ask_consent_update)

        yes_update = self._create_update_with_text('yes')
        yes_update.message.reply_to_message = ask_consent_update.message.message_id

        self.updater.dispatcher.process_update(yes_update)

        self.assertTrue(highlights.yc.called)
        self.assertEqual('the following highlights are available:\n'
                         'A: 1\n'
                         'really send?\n'
                         'highlights posted to yammer: [Die Südsterne in %s:\n' % current_calendar_week() +
                         'A: 1]', self.registry.writer_factory.writer.message)

    def test_not_sending_highlights_with_no(self):
        highlights = Highlights()
        highlights.yc = YammerTestConnector()
        highlights.add_pattern('A', '#highlights 1')

        assert len(highlights.highlights) == 1, highlights.highlights
        handler = self.registry.register_action(SendHighlightsConversationAction(highlights),
                                                FailureThrowingConversationActionHandler)

        ask_consent_update = self._create_update_with_text('/send_highlights')

        self.updater.dispatcher.process_update(ask_consent_update)
        assert handler.conversations[(1, 1)] == 1

        yes_update = self._create_update_with_text('no')
        yes_update.message.reply_to_message = ask_consent_update.message.message_id

        self.updater.dispatcher.process_update(yes_update)
        assert handler.conversations == {}

        self.assertFalse(highlights.yc.called)
        self.assertEqual('the following highlights are available:\n'
                         'A: 1\n'
                         'really send?\n'
                         'ok, not sending highlights.', self.registry.writer_factory.writer.message)


class TestCheckHighlights(TelegramBotTest):
    def test_collect_username(self):
        member = self.updater.bot.get_chat_administrators(1)
        member_list = list(map(lambda chat_member: chat_member.user.first_name, member))
        self.assertEqual(2, len(member_list))

    def test_collect_highlights_diff(self):
        member = self.updater.bot.get_chat_administrators(1)
        member_list = list(map(lambda chat_member: chat_member.user.first_name, member))

        highlights = Highlights()
        highlights.add_pattern('First', '#highlights test')

        remaining_user = list(filter(lambda user: not highlights.get(user), member_list))
        self.assertEqual(1, len(remaining_user))
        self.assertEqual('Second', remaining_user[0])
