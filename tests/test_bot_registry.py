import unittest

from telegram import Update, Message, Chat
from telegram.ext import Updater, CommandHandler

from tests.telegram_test_bot import TelegramTestBot


class Writer(object):
    def out(self, message):
        pass


class TelegramWriter(Writer):

    def __init__(self, bot):
        self.__bot=bot

    def out(self, message):
        self.__bot.send_message()


class CommandActionHandler(CommandHandler):
    def __init__(self, action, writer, *args, **kwargs):
        super(CommandActionHandler, self).__init__(action.name, action.command(), *args, **kwargs)
        self.__action = action
        self.__writer = writer

    def handle_update(self, update, dispatcher):
        return self.callback(self.__writer)


class BotRegistry(object):
    def __init__(self, updater):
        self.__updater = updater

    def register_command_action(self, action):
        self.__updater.dispatcher.add_handler(CommandActionHandler(action, None))


class TestCommandAction(object):
    def __init__(self):
        self.__called = False

    def command(self):
        return self.callback_command

    @property
    def name(self):
        return 'test'

    def callback_command(self, writer):
        self.__called = True
        writer.out('test call')

    def was_called(self):
        return self.__called


class TestBotRegistry(unittest.TestCase):
    def test_add_action_listener(self):
        updater = Updater(bot=TelegramTestBot())

        BotRegistry(updater).register_command_action(TestCommandAction())

        self.assertEqual(1, len(updater.dispatcher.handlers.keys()))

    def test_command_callable(self):
        updater = Updater(bot=TelegramTestBot())
        action = TestCommandAction()
        handler = CommandActionHandler(action, Writer())

        handler.handle_update(Update(1, Message(1, None, None, Chat(1, None), text='test', bot=self)),
                              updater.dispatcher)

        self.assertTrue(action.was_called())

    def test_action_writes_to_bot(self):
        bot = TelegramTestBot()
        updater = Updater(bot=bot)
        action = TestCommandAction()
        writer = TelegramWriter(bot)

        self.called = False
        bot.send_message = self.log_call

        handler = CommandActionHandler(action, writer)

        handler.handle_update(Update(1, Message(1, None, None, Chat(1, None), text='test', bot=self)),
                              updater.dispatcher)

        self.assertTrue(self.called)

    def log_call(self):
        self.called = True
