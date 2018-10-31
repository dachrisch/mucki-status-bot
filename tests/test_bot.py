# coding=utf-8
import re
import unittest

from telegram.ext import CommandHandler, RegexHandler

from tests.telegram_test_bot import TelegramBotTest
from yammer_service.highlights import HIGHLIGHTS_PATTERN


class TestBot(TelegramBotTest):
    def setUp(self):
        super().setUp()
        from telegram_service.bot import register_commands
        register_commands(self.updater)
        self.available_commands = list(map(lambda x: x.command[0],
                                           list(filter(lambda x: isinstance(x, CommandHandler),
                                                       self.updater.dispatcher.handlers[0]))))

    def test_start_available(self):
        self.assertIn('start', self.available_commands)

    def test_help_available(self):
        self.assertIn('help', self.available_commands)

    def test_howarewe_available(self):
        self.assertIn('howarewe', self.available_commands)

    def test_show_highlights_available(self):
        self.assertIn('show_highlights', self.available_commands)

    @unittest.skip('not available currently')
    def test_deals_available(self):
        self.assertIn('deals', self.available_commands)

    def test_remote_available(self):
        self.assertIn('remote', self.available_commands)

    def test_highlights_available(self):
        from telegram_service.bot import register_commands
        register_commands(self.updater)
        self.available_commands = list(map(lambda x: x.pattern,
                                           list(filter(lambda x: isinstance(x, RegexHandler),
                                                       self.updater.dispatcher.handlers[0]))))

        self.assertIn(re.compile(HIGHLIGHTS_PATTERN), self.available_commands)


@unittest.skip("Request faild: https://api.pipedrive.com/v1/stages?pipeline_id=5&api_"
               "token={'success': False, 'error': 'unauthorized access', 'errorCode': 401}")
class TestDeals(TelegramBotTest):
    def test_can_execute_deals(self):
        self.assert_can_execute_command('deals')


class TestHighlights(TelegramBotTest):
    def test_can_execute_send_highlights(self):
        self.assert_can_execute_command('send_highlights')
