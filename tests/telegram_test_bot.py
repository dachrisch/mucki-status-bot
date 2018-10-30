# coding=utf-8
from telegram import Bot, Update, Message, Chat
from telegram.ext import Dispatcher, CommandHandler, Updater

from telegram_service import bot
from telegram_service.bot import BotRegistry, CommandActionHandler
from telegram_service.writer import Writer, WriterFactory


class FailureThrowingCommandHandler(CommandHandler):
    def __init__(self,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.catched_error = None

    def handle_update(self, update, dispatcher):
        try:
            super().handle_update(update, dispatcher)
        except Exception as e:
            self.catched_error = e


class FailureThrowingCommandActionHandler(CommandActionHandler):
    def __init__(self,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.catched_error = None

    def handle_update(self, update, dispatcher):
        try:
            super().handle_update(update, dispatcher)
        except BaseException as e:
            self.catched_error = e


class TelegramTestBot(Bot):

    def __init__(self):
        Bot.__init__(self, '1234:abcd1234')
        self.bot = _EncapsulatedTelegramTestBot()
        self.dispatcher = Dispatcher(self, None)
        self.__test_value = False
        self.send_message = None

    def assert_can_execute_command(self, this_unittest, command):
        """
        :type this_unittest: unittest.TestCase
        :type command: str
        """
        self.send_message = self._assert_called

        handler = self._add_handler(command)

        self.dispatcher.process_update(self._create_update_with_text('/' + command))

        self._check_handler(handler)

        this_unittest.assertTrue(self.__test_value)

    def assert_command_responses_with(self, this_unittest, command, expected_text):
        """
        :type this_unittest: unittest.TestCase
        :type command: str
        :type expected_text: str
        """
        self.send_message = self._assert_message_test

        handler = self._add_handler(command)

        self.dispatcher.process_update(self._create_update_with_text('/' + command))

        self._check_handler(handler)
        this_unittest.assertIn(expected_text, self.__test_value)

    def assert_command_action_responses_with(self, this_unittest, action, expected_containing_message):
        """
        :type this_unittest: unittest.TestCase
        :type action: service.action.CommandActionMixin
        :type expected_containing_message: str
        """
        updater = Updater(bot=self)
        registry = BotRegistry(updater)
        registry.writer_factory = LoggingWriterFactory()

        handler = registry.register_command_action(action, action_handler_class=FailureThrowingCommandActionHandler)

        updater.dispatcher.process_update(self._create_update_with_text('/' + action.name))

        self._check_handler(handler)

        this_unittest.assertIn(expected_containing_message, registry.writer_factory.writer.message)

    def _check_handler(self, handler):
        if handler.catched_error:
            raise handler.catched_error

    def _add_handler(self, command):
        handler = FailureThrowingCommandHandler(command, getattr(bot, command))
        self.dispatcher.add_handler(handler)
        return handler

    def _create_update_with_text(self, text):
        return Update(1, Message(1, None, None, Chat(1, None), text=text, bot=self))

    def _assert_called(self, *args, **kwargs):
        self.__test_value = True

    def _assert_message_test(self, *args, **kwargs):
        self.__test_value = args[1]

    def send_chat_action(self, chat_id, action, timeout=None, **kwargs):
        self.__test_value = 'chat_action'

    def send_sticker(self,
                     chat_id,
                     sticker,
                     disable_notification=False,
                     reply_to_message_id=None,
                     reply_markup=None,
                     timeout=20,
                     **kwargs):
        # self.__test_value = 'sticker'
        pass


class LoggingWriter(Writer):
    def __init__(self):
        self.message = ''

    def out(self, message):
        self.message += message


class LoggingWriterFactory(WriterFactory):
    def __init__(self):
        self.writer = LoggingWriter()

    def create(self, *args, **kwargs):
        return self.writer


class _EncapsulatedTelegramTestBot(object):
    def __init__(self):
        self.username = 'test'
