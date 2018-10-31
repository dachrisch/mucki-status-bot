from google_service_api.welfare import WelfareCommandAction, WelfareStatus
from telegram_service.gif import GifRetriever
from tests.telegram_test_bot import TelegramBotTest
from tests.test_status import DummySheetConnector


class DummyGifRetriever(GifRetriever):
    def random_gif_url(self, query):
        return 'http://test.url'


class TestHowAreWe(TelegramBotTest):
    def test_can_execute_howarewe(self):
        command_action = WelfareCommandAction()
        command_action.welfare_status = WelfareStatus(DummySheetConnector((('A', 'OK', 1, 2),)))
        command_action.gif_retriever = DummyGifRetriever()
        self.assert_command_action_responses_with(command_action,
                                                  'calculating welfare status of team...\n'
                                                  'A is OK (1, 2)\n'
                                                  '####### !UNICORN DANCE! ########\n'
                                                  'http://test.url')
