# coding=UTF-8

from config import MUC_TELEGRAM_GROUP_ID
from google_service_api.welfare import WelfareCommandAction
from help_service.help import HelpCommandAction, StartCommandAction
from order_service.orders import OrdersCommandAction
from remote_service.remotes import RemoteMethodCommandAction
from telegram_service.handler import CommandActionHandler, RegexActionHandler, ConversationActionHandler
from telegram_service.retriever import AdminRetriever
from telegram_service.writer import TelegramWriterFactory
from yammer_service.highlights import Highlights, ShowHighlightsCommandAction, \
    HighlightsCollectorRegexAction, SendHighlightsConversationAction, CheckHighlightsCommandAction, \
    HighlightsForCommandAction

log = None


class BotRegistry(object):
    def __init__(self, updater):
        """
        :type updater: telegram.ext.updater.Updater
        """
        self.__updater = updater
        self.writer_factory = TelegramWriterFactory(updater.bot)
        self.__registered_actions = []
        self.highlights = Highlights()

    def register_command_action(self, action):
        return self.register_action(action, CommandActionHandler)

    def register_regex_action(self, action):
        return self.register_action(action, RegexActionHandler)

    def register_conversation_action(self, action):
        return self.register_action(action, ConversationActionHandler)

    def register_action(self, action, action_handler_class):
        """
        :type action: service.action.ActionMixin
        :type action_handler_class: type[telegram_service.handler.ActionHandler]
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
        self.register_command_action(ShowHighlightsCommandAction(self.highlights))
        self.register_regex_action(HighlightsCollectorRegexAction(self.highlights))
        self.register_conversation_action(
            SendHighlightsConversationAction(self.highlights,
                                             AdminRetriever(self.__updater, MUC_TELEGRAM_GROUP_ID).admin_member))
        self.register_command_action(
            CheckHighlightsCommandAction(self.highlights,
                                         AdminRetriever(self.__updater, MUC_TELEGRAM_GROUP_ID).admin_member))
        self.register_command_action(HighlightsForCommandAction(self.highlights))
