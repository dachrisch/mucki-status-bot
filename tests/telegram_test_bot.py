# coding=utf-8
from telegram import Bot, Update, Message, Chat
from telegram.ext import Dispatcher, CommandHandler

from telegram_service import bot


class TelegramTestBot(Bot):

    def __init__(self):
        Bot.__init__(self, '1234:abcd1234')
        self.bot = _EncapsulatedTelegramTestBot()
        self.dispatcher = Dispatcher(self, None)
        self.__test_value = False
        self.send_message = None

    def assert_can_execute_command(self, this_unittest, command):
        self.send_message = self._assert_called

        self.dispatcher.add_handler(CommandHandler(command, getattr(bot, command)))

        self.dispatcher.process_update(self._create_update_with_text('/' + command))
        this_unittest.assertTrue(self.__test_value)

    def assert_command_responses_with(self, this_unittest, command, expected_text):
        self.send_message = self._assert_message_test

        self.dispatcher.add_handler(CommandHandler(command, getattr(bot, command)))

        self.dispatcher.process_update(self._create_update_with_text('/' + command))
        this_unittest.assertIn(expected_text, self.__test_value)

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


class _EncapsulatedTelegramTestBot(object):
    def __init__(self):
        self.username = 'test'
