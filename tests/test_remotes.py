# coding=utf-8
import unittest

from remote_service.remotes import RemoteMethodCommandAction
from tests.telegram_test_bot import TelegramTestBot


class TestRemotes(unittest.TestCase):
    def test_remote_chat_room(self):
        action = RemoteMethodCommandAction()
        expected_containing_message = 'https://zoom.us/j/6787719716'

        TelegramTestBot().assert_command_action_responses_with(self, action, expected_containing_message)
