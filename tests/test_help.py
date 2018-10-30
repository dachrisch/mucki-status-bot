# coding=utf-8
import unittest

from telegram.ext import Updater

from help_service.help import HelpCommandAction, StartCommandAction
from telegram_service.bot import BotRegistry
from tests.telegram_test_bot import TelegramTestBot
from tests.test_bot_registry import CommandTestAction


class TestHelp(unittest.TestCase):
    def test_help(self):
        action = StartCommandAction()
        expected_containing_message = action.help_text

        TelegramTestBot().assert_command_action_responses_with(self, action, expected_containing_message)

    def test_help_text(self):
        bot = TelegramTestBot()
        updater = Updater(bot=bot)

        registry = BotRegistry(updater)
        registry.register_command_action(CommandTestAction('test', 'help text'))
        help_command_action = HelpCommandAction(registry)
        bot.assert_command_action_responses_with(self, help_command_action,
                                                 '%s\n%s' % (help_command_action.help_text, 'help text'))
