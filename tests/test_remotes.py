# coding=utf-8

from remote_service.client import RemoteMethodCommandAction
from service.api import ApiRetriever
from tests.telegram_test_bot import TelegramBotTest


class ApiTestRetriever(ApiRetriever):
    class _ApiTestInvoker(object):
        def __init__(self, actual_return):
            self.actual_return = actual_return

        @property
        def get(self):
            return self.actual_return

    def __init__(self, actual_return):
        self.actual_return = actual_return

    def with_method(self, method):
        return ApiTestRetriever._ApiTestInvoker(self.actual_return)


class TestRemotesNewServiceWithApi(TelegramBotTest):

    def test_remote_chat_room(self):
        action = RemoteMethodCommandAction()
        action.api_invoker = ApiTestRetriever(
            ({'name': 'Test', 'login': 'test_login', 'remote': 'https://zoom.us/j/6787719716'},))
        self.assert_command_action_responses_with(action, 'https://zoom.us/j/6787719716')
