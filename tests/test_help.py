# coding=utf-8
import unittest

from telegram.ext import Updater

from help_service.help import HelpCommandAction
from telegram_service.bot import BotRegistry, register_commands
from tests.telegram_test_bot import TelegramTestBot
from tests.test_bot_registry import CommandTestAction


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
                                                 'The following commands are available:\n'
                                                 '/help - Prints the help message\n'
                                                 '/start - Starts the bot\n'
                                                 '/remote - displays all options for remote meetings')
