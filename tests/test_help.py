# coding=utf-8

from telegram.ext import Updater

from google_service_api.welfare import WelfareCommandAction
from help_service.help import HelpCommandAction, StartCommandAction
from invoice_service.invoices import InvoiceCommandAction
from order_service.orders import OrdersCommandAction
from remote_service.client import RemoteMethodCommandAction
from telegram_service.bot import BotRegistry
from tests.telegram_test_bot import TelegramBotTest
from tests.test_bot_registry import CommandTestAction
from yammer_service.highlights import ShowHighlightsCommandAction, HighlightsCollectorRegexAction, \
    SendHighlightsConversationAction, CheckHighlightsCommandAction, HighlightsForCommandAction


class TestHelp(TelegramBotTest):
    def test_help_text(self):
        self.registry.register_command_action(CommandTestAction('test', 'help text'))
        help_command_action = HelpCommandAction(self.registry)
        self.assert_command_action_responses_with(help_command_action,
                                                  'test - help text')

    def test_full_help_text(self):
        updater = Updater(bot=self.bot)

        registry = BotRegistry(updater)
        registry.register_commands()
        help_command_action = HelpCommandAction(registry)
        self.assert_command_action_responses_with(help_command_action,
                                                  'The following commands are available:'
                                                  + '\n' + HelpCommandAction(None).help_entry
                                                  + '\n' + StartCommandAction().help_entry
                                                  + '\n' + RemoteMethodCommandAction().help_entry
                                                  + '\n' + OrdersCommandAction().help_entry
                                                  + '\n' + WelfareCommandAction().help_entry
                                                  + '\n' + ShowHighlightsCommandAction(None).help_entry
                                                  + '\n' + HighlightsCollectorRegexAction(None).help_entry
                                                  + '\n' + SendHighlightsConversationAction(None, None).help_entry
                                                  + '\n' + CheckHighlightsCommandAction(None, None).help_entry
                                                  + '\n' + HighlightsForCommandAction(None).help_entry
                                                  + '\n' + InvoiceCommandAction().help_entry
                                                  )
