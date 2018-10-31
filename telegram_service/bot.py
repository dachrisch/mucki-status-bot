# coding=UTF-8
from abc import ABC

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
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
from yammer_service.highlights import Highlights, HIGHLIGHTS_PATTERN, HighlightsCommandAction

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


def collect_highlight(bot, update):
    user = UpdateRetriever(update).user
    if highlights.add(user, str(update.message.text)):
        _send_and_log(bot, update, 'collecting highlight for %s: [%s]' % (user, highlights.get(user)))


def show_highlights(bot, update):
    if highlights.is_not_empty():
        _send_and_log(bot, update, 'the following highlights are available:\n%s' % highlights.message_string)
    else:
        _send_and_log(bot, update, 'no highlights available')


def ask_for_consent(bot, update):
    show_highlights(bot, update)
    reply_keyboard = [['yes', 'no']]
    if highlights.is_not_empty():
        _send_and_log(bot, update, 'really send?',
                      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return 1
    else:
        return ConversationHandler.END


def send_highlights(bot, update):
    if update.message.text == 'yes':
        try:
            message_url = highlights.send_to_yammer()
            _send_and_log(bot, update, 'highlights posted to yammer: [%s]' % message_url,
                          reply_markup=ReplyKeyboardRemove())
        except Exception as e:
            _send_and_log(bot, update, 'failed to post to yammer: [%s]' % e, reply_markup=ReplyKeyboardRemove())

        highlights.clear()
    else:
        cancel(bot, update)
    return ConversationHandler.END


def cancel(bot, update):
    _send_and_log(bot, update, 'ok, not sending highlights.', reply_markup=ReplyKeyboardRemove())


def register_commands(updater):
    registry = BotRegistry(updater)
    registry.register_command_action(HelpCommandAction(registry))
    registry.register_command_action(StartCommandAction())
    registry.register_command_action(RemoteMethodCommandAction())
    registry.register_command_action(OrdersCommandAction())
    registry.register_command_action(WelfareCommandAction())
    registry.register_command_action(HighlightsCommandAction(highlights))

    dp = updater.dispatcher
    dp.add_handler(RegexHandler(HIGHLIGHTS_PATTERN, collect_highlight))
    dp.add_error_handler(error)
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('send_highlights', ask_for_consent)],
        states={
            1: [RegexHandler('^(yes|no)$', send_highlights)],
        },
        fallbacks=[Handler(cancel)]

    ))
    return registry


def _send_and_log(bot, update, message, reply_markup=None):
    global log
    log = get_logger(__name__)
    bot.send_message(UpdateRetriever(update).chat_id, message, reply_markup=reply_markup, disable_web_page_preview=True)
    log.info(message)


def error(bot, update, _error):
    """Log Errors caused by Updates."""
    log.warning('Update "%s" caused error "%s"', update, _error)


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
            self.callback(writer)
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
            self.callback(update_retriever, writer)
        except Exception as e:
            writer.out_error(e)
            raise e


class BotRegistry(object):
    def __init__(self, updater):
        """
        :type updater: telegram.ext.updater.Updater
        """
        self.__updater = updater
        self.writer_factory = TelegramWriterFactory(updater.bot)
        self.__registered_actions = []

    def register_command_action(self, action, action_handler_class=CommandActionHandler):
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
