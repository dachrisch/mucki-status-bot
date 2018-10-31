# coding=utf-8

from remote_service.remotes import RemoteMethodCommandAction
from tests.telegram_test_bot import TelegramBotTest


class TestRemotes(TelegramBotTest):
    def test_remote_chat_room(self):
        self.assert_command_action_responses_with(RemoteMethodCommandAction(), 'https://zoom.us/j/6787719716')
