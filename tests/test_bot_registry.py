import unittest

from telegram import Update, Message, Chat
from telegram.ext import Updater

from service.action import CommandActionMixin
from telegram_service.bot import BotRegistry, CommandActionHandler
from telegram_service.writer import WriterFactory, TelegramWriterFactory
from tests.telegram_test_bot import TelegramTestBot


class CommandTestAction(CommandActionMixin):
    @property
    def help_text(self):
        return self._help_text

    def __init__(self, name, help_text):
        self._help_text = help_text
        self._name = name

        self.__called = False

    def _writer_callback(self, writer):
        self.__called = True
        writer.out('test call')

    def was_called(self):
        return self.__called

    @property
    def name(self):
        return self._name


class TestBotRegistry(unittest.TestCase):
    def test_add_action_listener(self):
        updater = Updater(bot=TelegramTestBot())

        BotRegistry(updater).register_command_action(CommandTestAction('test', 'help text'))

        self.assertEqual(1, len(updater.dispatcher.handlers.keys()))

    def test_command_callable(self):
        updater = Updater(bot=TelegramTestBot())
        action = CommandTestAction('test', 'help text')
        handler = CommandActionHandler(action, WriterFactory())

        handler.handle_update(Update(1, Message(1, None, None, Chat(1, None), text='test', bot=self)),
                              updater.dispatcher)

        self.assertTrue(action.was_called())

    def test_action_writes_to_bot(self):
        bot = TelegramTestBot()
        updater = Updater(bot=bot)
        action = CommandTestAction('test', 'help text')
        writer_factory = TelegramWriterFactory(bot)

        self.called = False
        bot.send_message = self.log_call

        handler = CommandActionHandler(action, writer_factory)

        handler.handle_update(Update(1, Message(1, None, None, Chat(1, None), text='test', bot=self)),
                              updater.dispatcher)

        self.assertTrue(self.called)

    def log_call(self, *args, **kwargs):
        self.called = True
