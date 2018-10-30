# coding=utf-8
import unittest
from unittest.mock import PropertyMock

from telegram.ext import Updater, CommandHandler

from tests.telegram_test_bot import TelegramTestBot


class TestBot(unittest.TestCase):
    def setUp(self):
        from telegram_service.bot import register_commands
        updater = Updater(bot=TelegramTestBot())
        register_commands(updater)
        self.available_commands = list(map(lambda x: x.command[0],
                                           list(filter(lambda x: isinstance(x, CommandHandler),
                                                       updater.dispatcher.handlers[0]))))

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


@unittest.skip("Request faild: https://api.pipedrive.com/v1/stages?pipeline_id=5&api_"
               "token={'success': False, 'error': 'unauthorized access', 'errorCode': 401}")
class TestDeals(unittest.TestCase):
    def test_can_execute_deals(self):
        TelegramTestBot().assert_can_execute_command(self, 'deals')

    def test_deals_messages_all_right(self):
        TelegramTestBot().assert_command_responses_with(self, 'deals', 'interpretation')


class TestHowareWe(unittest.TestCase):
    def test_can_execute_howarewe(self):
        TelegramTestBot().assert_can_execute_command(self, 'howarewe')


class TestHighlights(unittest.TestCase):

    def test_can_execute_show_highlights(self):
        TelegramTestBot().assert_can_execute_command(self, 'show_highlights')

    def test_can_execute_send_highlights(self):
        TelegramTestBot().assert_can_execute_command(self, 'send_highlights')

    def test_no_highlights(self):
        TelegramTestBot().assert_command_responses_with(self, 'show_highlights', 'no highlights available')

    def test_one_highlight(self):
        from telegram_service.bot import highlights

        highlights.add('Chris', '#highlights one')
        TelegramTestBot().assert_command_responses_with(self, 'show_highlights', 'Chris: one')

    def test_howarewe_all_ok(self):
        from unittest import mock
        with mock.patch('google_service_api.welfare.WelfareStatus.team_name_status',
                        new_callable=PropertyMock) as team_status_mock:
            team_status_mock.return_value = (('A', 'OK', None, None),
                                             ('B', 'OK', None, None),
                                             ('C', 'OK', None, None),
                                             ('D', 'OK', None, None),
                                             ('E', 'OK', None, None),
                                             ('F', 'OK', None, None),
                                             ('G', 'OK', None, None),
                                             ('H', 'OK', None, None))
            TelegramTestBot().assert_command_responses_with(self, 'howarewe', '####### !UNICORN DANCE! ########')
            team_status_mock.assert_any_call()
