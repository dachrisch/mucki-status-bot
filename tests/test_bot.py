# coding=utf-8
import unittest
from unittest.mock import PropertyMock

from tests.telegram_test_bot import TelegramTestBot


class TestBot(unittest.TestCase):
    def test_can_execute_start(self):
        TelegramTestBot().assert_can_execute_command(self, 'start')

    def test_start_messages_hello(self):
        TelegramTestBot().assert_command_responses_with(self, 'start', "I'm the bot of the *Südsterne* team.")


@unittest.skip("Request faild: https://api.pipedrive.com/v1/stages?pipeline_id=5&api_"
               "token={'success': False, 'error': 'unauthorized access', 'errorCode': 401}")
class TestDeals(unittest.TestCase):
    def test_can_execute_deals(self):
        TelegramTestBot().assert_can_execute_command(self, 'deals')

    def test_deals_messages_all_right(self):
        TelegramTestBot().assert_command_responses_with(self, 'deals', 'interpretation')


class TestRemotes(unittest.TestCase):
    def test_remote_chat_room(self):
        TelegramTestBot().assert_command_responses_with(self, 'remote', 'https://zoom.us/j/6787719716')


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
            team_status_mock.return_value = (('A', 'OK', None, None, None, None),
                                             ('B', 'OK', None, None, None, None),
                                             ('C', 'OK', None, None, None, None),
                                             ('D', 'OK', None, None, None, None),
                                             ('E', 'OK', None, None, None, None),
                                             ('F', 'OK', None, None, None, None),
                                             ('G', 'OK', None, None, None, None),
                                             ('H', 'OK', None, None, None, None))
            TelegramTestBot().assert_command_responses_with(self, 'howarewe', '####### !UNICORN DANCE! ########')
            team_status_mock.assert_any_call()
