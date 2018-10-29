# coding=utf-8
import unittest

from help_service.help import HelpCommandAction
from remote_service.remotes import RemoteMethodCommandAction
from tests.telegram_test_bot import TelegramTestBot


class TestHelp(unittest.TestCase):
    def test_help(self):
        action = HelpCommandAction()
        expected_containing_message = "I'm the bot of the *Südsterne* team."

        TelegramTestBot().assert_command_action_responses_with(self, action, expected_containing_message)
