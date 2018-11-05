# coding=UTF-8
from abc import ABC

from telegram.ext import (CommandHandler, RegexHandler,
                          ConversationHandler, Handler)

from config import MUCKI_TRACKER_SHEET_ID, MUC_TELEGRAM_GROUP_ID
from google_service.sheets import SheetConnector
from google_service_api.welfare import WelfareStatus, WelfareCommandAction
from help_service.help import HelpCommandAction, StartCommandAction
from order_service.orders import OrdersCommandAction
from remote_service.remotes import RemoteMethodCommandAction
from telegram_service.retriever import UpdateRetriever, AdminRetriever
from telegram_service.writer import TelegramWriterFactory
from yammer_service.highlights import Highlights, ShowHighlightsCommandAction, \
    HighlightsCollectorRegexAction, SendHighlightsConversationAction, CheckHighlightsCommandAction

log = None
highlights = Highlights()
welfare_status = WelfareStatus(SheetConnector(MUCKI_TRACKER_SHEET_ID))


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

    def register_commands(self):
        self.register_command_action(HelpCommandAction(self))
        self.register_command_action(StartCommandAction())
        self.register_command_action(RemoteMethodCommandAction())
        self.register_command_action(OrdersCommandAction())
        self.register_command_action(WelfareCommandAction())
        self.register_command_action(ShowHighlightsCommandAction(highlights))
        self.register_regex_action(HighlightsCollectorRegexAction(highlights))
        self.register_conversation_action(
            SendHighlightsConversationAction(highlights,
                                             AdminRetriever(self.__updater, MUC_TELEGRAM_GROUP_ID).admin_member))
        self.register_command_action(
            CheckHighlightsCommandAction(highlights,
                                         AdminRetriever(self.__updater, MUC_TELEGRAM_GROUP_ID).admin_member))
