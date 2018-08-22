# coding=utf-8
import unittest

from tests.telegram_test_bot import TelegramTestBot


class TestHighlights(unittest.TestCase):
    def test_can_execute_start(self):
        TelegramTestBot().assert_can_execute_command(self, 'start')

    def test_can_execute_howarewe(self):
        TelegramTestBot().assert_can_execute_command(self, 'howarewe')

    def test_can_execute_show_highlights(self):
        TelegramTestBot().assert_can_execute_command(self, 'show_highlights')

    def test_can_execute_send_highlights(self):
        TelegramTestBot().assert_can_execute_command(self, 'send_highlights')

    def test_can_execute_deals(self):
        TelegramTestBot().assert_can_execute_command(self, 'deals')

    def test_start_messages_hello(self):
        TelegramTestBot().assert_command_responses_with(self, 'start', "I'm the bot of the *Südsterne* team.")

    def test_no_highlights(self):
        TelegramTestBot().assert_command_responses_with(self, 'show_highlights', 'no highlights available')

    def test_one_highlight(self):
        from telegram_service.bot import highlights

        highlights.add('Chris', '#highlights one')
        TelegramTestBot().assert_command_responses_with(self, 'show_highlights', 'Chris: one')

    def test_deals_messages_all_right(self):
        TelegramTestBot().assert_command_responses_with(self, 'deals', 'Alles rosig!')
