# coding=UTF-8
from abc import ABC

from telegram.ext import (CommandHandler, RegexHandler,
                          ConversationHandler, Handler)

from config import MUCKI_TRACKER_SHEET_ID
from google_service.sheets import SheetConnector
from google_service_api.welfare import WelfareStatus, WelfareCommandAction
from help_service.help import HelpCommandAction, StartCommandAction
from my_logging import get_logger
from order_service.orders import OrdersCommandAction
from remote_service.remotes import RemoteMethodCommandAction
from telegram_service.writer import TelegramWriterFactory
from yammer_service.highlights import Highlights, ShowHighlightsCommandAction, \
    HighlightsCollectorRegexAction, SendHighlightsConversationAction

log = None
highlights = Highlights()
welfare_status = WelfareStatus(SheetConnector(MUCKI_TRACKER_SHEET_ID))


class UpdateRetriever(object):
    def __init__(self, update):
        """

        :type update: telegram.Update
        """
        self._update = update

    @property
    def chat_id(self):
        return self._update.message.chat_id

    @property
    def user(self):
        return self._update.message.from_user.first_name

    @property
    def message(self):
        return self._update.message.text


def register_commands(updater):
    registry = BotRegistry(updater)
    registry.register_command_action(HelpCommandAction(registry))
    registry.register_command_action(StartCommandAction())
    registry.register_command_action(RemoteMethodCommandAction())
    registry.register_command_action(OrdersCommandAction())
    registry.register_command_action(WelfareCommandAction())
    registry.register_command_action(ShowHighlightsCommandAction(highlights))
    registry.register_regex_action(HighlightsCollectorRegexAction(highlights))
    registry.register_conversation_action(SendHighlightsConversationAction(highlights))
    return registry


def _send_and_log(bot, update, message, reply_markup=None):
    global log
    log = get_logger(__name__)
    bot.send_message(UpdateRetriever(update).chat_id, message, reply_markup=reply_markup, disable_web_page_preview=True)
    log.info(message)


class ActionHandler(Handler, ABC):
    def __init__(self, action, writer_factory, *args, **kwargs):
        """
        :type action: service.action.ActionMixin
        :type writer_factory: telegram_service.writer.WriterFactory
        """
        Handler.__init__(self, action.callback_function, *args, **kwargs)
        self.action = action
        self.writer_factory = writer_factory


class CommandActionHandler(ActionHandler, CommandHandler):
    def __init__(self, action, writer_factory, *args, **kwargs):
        """
        :type action: service.action.CommandActionMixin
        :type writer_factory: telegram_service.writer.WriterFactory
        """
        ActionHandler.__init__(self, action, writer_factory, *args, **kwargs)
        CommandHandler.__init__(self, action.command, action.callback_function, *args, **kwargs)

    def handle_update(self, update, dispatcher):
        """
        :type update: telegram.Update
        :type dispatcher telegram.ext.Dispatcher
        """
        writer = self.writer_factory.create(UpdateRetriever(update).chat_id)
        try:
            return self.callback(writer)
        except Exception as e:
            writer.out_error(e)
            raise e


class RegexActionHandler(ActionHandler, RegexHandler):
    def __init__(self, action, writer_factory, *args, **kwargs):
        """
        :type action: service.action.RegexActionMixin
        :type writer_factory: telegram_service.writer.WriterFactory
        """
        ActionHandler.__init__(self, action, writer_factory, *args, **kwargs)
        RegexHandler.__init__(self, action.pattern, action.callback_function, *args, **kwargs)

    def handle_update(self, update, dispatcher):
        """
        :type update: telegram.Update
        :type dispatcher telegram.ext.Dispatcher
        """
        update_retriever = UpdateRetriever(update)
        writer = self.writer_factory.create(update_retriever.chat_id)
        try:
            return self.callback(update_retriever, writer)
        except Exception as e:
            writer.out_error(e)
            raise e


class ConversationActionHandler(ActionHandler, ConversationHandler):
    def __init__(self, conversation_action, writer_factory, *args, **kwargs):
        """

        :type conversation_action: ConversationActionMixin
        :type writer_factory: telegram_service.writer.WriterFactory
        """
        ActionHandler.__init__(self, conversation_action, writer_factory, *args, **kwargs)
        ConversationHandler.__init__(self,
                                     entry_points=[
                                         CommandActionHandler(conversation_action.entry_action, writer_factory)],
                                     states={
                                         1: [RegexActionHandler(conversation_action.yes_callback, writer_factory)],
                                     },
                                     fallbacks=[Handler(conversation_action.no_callback)]
                                     )


class BotRegistry(object):
    def __init__(self, updater):
        """
        :type updater: telegram.ext.updater.Updater
        """
        self.__updater = updater
        self.writer_factory = TelegramWriterFactory(updater.bot)
        self.__registered_actions = []

    def register_command_action(self, action):
        return self.register_action(action, CommandActionHandler)

    def register_regex_action(self, action):
        return self.register_action(action, RegexActionHandler)

    def register_conversation_action(self, action):
        return self.register_action(action, ConversationActionHandler)

    def register_action(self, action, action_handler_class):
        """
        :type action: service.action.ActionMixin
        :type action_handler_class: type[telegram_service.bot.ActionHandler]
        """
        handler = action_handler_class(action, self.writer_factory)
        self.__updater.dispatcher.add_handler(handler)
        self.__registered_actions.append(action)
        return handler

    @property
    def registered_actions(self):
        """
        :rtype: list[service.action.CommandActionMixin]
        """
        return self.__registered_actions