# coding=utf-8
from multiprocessing import Process
from unittest import TestCase

import jsonpickle

from remote_service.client import NewRemoteMethodCommandAction
from remote_service.remotes import RemoteMethodCommandAction
from remote_service.service import remote_app
from tests.telegram_test_bot import TelegramBotTest


class TestRemotes(TelegramBotTest):
    def test_remote_chat_room(self):
        self.assert_command_action_responses_with(RemoteMethodCommandAction(), 'https://zoom.us/j/6787719716')


class TestRemotesNewServiceWithApi(TelegramBotTest):
    def setUp(self):
        super().setUp()
        # creates a test client
        self.server = Process(target=remote_app.run)
        self.server.start()

    def tearDown(self):
        self.server.terminate()
        self.server.join()

    def test_remote_chat_room(self):
        self.assert_command_action_responses_with(NewRemoteMethodCommandAction(), 'https://zoom.us/j/6787719716')


class TestRemotesApi(TestCase):
    def setUp(self):
        # creates a test client
        self.app = remote_app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def test_get_remote_methods(self):
        self.assertEqual(200, self.app.get('/remotes/api/v1.0/methods').status_code)

    def test_methods_as_json(self):
        response = self.app.get('/remotes/api/v1.0/methods').data
        self.assertEqual(3, len(jsonpickle.decode(response)))
