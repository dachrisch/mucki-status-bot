# coding=utf-8

from remote_service.client import RemoteMethodCommandAction
from tests.api_test_retriever import ApiTestRetriever
from tests.telegram_test_bot import TelegramBotTest


class TestRemotesNewServiceWithApi(TelegramBotTest):

    def test_remote_chat_room(self):
        action = RemoteMethodCommandAction()
        action.api_invoker = ApiTestRetriever({'methods':
                                                   ({'name': 'Test', 'login': 'test_login',
                                                     'remote': 'https://zoom.us/j/6787719716'},)})
        self.assert_command_action_responses_with(action, 'https://zoom.us/j/6787719716')
