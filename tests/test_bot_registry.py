# coding=utf-8
from telegram import Update, Message, Chat

from service.action import CommandActionMixin
from telegram_service.handler import CommandActionHandler
from telegram_service.writer import WriterFactory
from tests.telegram_test_bot import TelegramBotTest


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


class TestBotRegistry(TelegramBotTest):
    def test_add_action_listener(self):
        self.registry.register_command_action(CommandTestAction('test', 'help text'))

        self.assertEqual(1, len(self.updater.dispatcher.handlers.keys()))

    def test_command_callable(self):
        action = CommandTestAction('test', 'help text')
        handler = CommandActionHandler(action, WriterFactory())

        handler.handle_update(Update(1, Message(1, None, None, Chat(1, None), text='test', bot=self)),
                              self.updater.dispatcher)

        self.assertTrue(action.was_called())

    def test_action_writes_to_bot(self):
        action = CommandTestAction('test', 'help text')

        handler = CommandActionHandler(action, self.registry.writer_factory)

        handler.handle_update(Update(1, Message(1, None, None, Chat(1, None), text='test', bot=self)),
                              self.updater.dispatcher)

        self.assertTrue(action.was_called())
