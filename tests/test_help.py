# coding=utf-8
import unittest

from telegram.ext import Updater

from google_service_api.welfare import WelfareCommandAction
from help_service.help import HelpCommandAction, StartCommandAction
from order_service.orders import OrdersCommandAction
from remote_service.remotes import RemoteMethodCommandAction
from telegram_service.bot import BotRegistry, register_commands
from tests.telegram_test_bot import TelegramTestBot
from tests.test_bot_registry import CommandTestAction
from yammer_service.highlights import ShowHighlightsCommandAction, HighlightsCollectorRegexAction


class TestHelp(unittest.TestCase):
    def test_help_text(self):
        bot = TelegramTestBot()
        updater = Updater(bot=bot)

        registry = BotRegistry(updater)
        registry.register_command_action(CommandTestAction('test', 'help text'))
        help_command_action = HelpCommandAction(registry)
        bot.assert_command_action_responses_with(self, help_command_action,
                                                 'test - help text')

    def test_full_help_text(self):
        bot = TelegramTestBot()
        updater = Updater(bot=bot)

        registry = register_commands(updater)
        help_command_action = HelpCommandAction(registry)
        bot.assert_command_action_responses_with(self, help_command_action,
                                                 'The following commands are available:'
                                                 + '\n' + HelpCommandAction(None).help_entry
                                                 + '\n' + StartCommandAction().help_entry
                                                 + '\n' + RemoteMethodCommandAction().help_entry
                                                 + '\n' + OrdersCommandAction().help_entry
                                                 + '\n' + WelfareCommandAction().help_entry
                                                 + '\n' + ShowHighlightsCommandAction(None).help_entry
                                                 + '\n' + HighlightsCollectorRegexAction(None).help_entry
                                                 )
