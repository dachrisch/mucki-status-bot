# coding=UTF-8
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (CommandHandler, RegexHandler,
                          ConversationHandler, Handler)

from config import MUCKI_TRACKER_SHEET_ID
from google_service.sheets import SheetConnector
from google_service_api.welfare import WelfareStatus
from help_service.help import HelpCommandAction, StartCommandAction
from my_logging import get_logger
from order_service.orders import OrdersCommandAction
from remote_service.remotes import RemoteMethodCommandAction
from telegram_service.gif import random_gif_url
from telegram_service.writer import TelegramWriterFactory
from yammer_service.highlights import Highlights, HIGHLIGHTS_PATTERN

log = None
highlights = Highlights()
welfare_status = WelfareStatus(SheetConnector(MUCKI_TRACKER_SHEET_ID))


class UpdateRetriever(object):
    def __init__(self, update):
        self._update = update

    @property
    def chat_id(self):
        return self._update.message.chat_id

    @property
    def user(self):
        return self._update.message.from_user.first_name


def howarewe(bot, update):
    try:
        _send_status(bot, update)
        _send_shoutout(bot, update)
    except Exception as e:
        _send_and_log(bot, update, 'failed to obtain status: [%s]' % e)


def collect_highlight(bot, update):
    user = UpdateRetriever(update).user
    if highlights.add(user, str(update.message.text)):
        _send_and_log(bot, update, 'collecting highlight for %s: [%s]' % (user, highlights.get(user)))


def show_highlights(bot, update):
    if highlights.is_not_empty():
        _send_and_log(bot, update, 'the following highlights are available:\n%s' % highlights.message_string())
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

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('howarewe', howarewe))
    dp.add_handler(RegexHandler(HIGHLIGHTS_PATTERN, collect_highlight))
    dp.add_handler(CommandHandler('show_highlights', show_highlights))
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


def _send_status(bot, update):
    _send_and_log(bot, update, 'calculating welfare status of team...')
    _thinking(bot, update)
    _send_and_log(bot, update, welfare_status.team_message)


def _send_shoutout(bot, update):
    global log
    log = get_logger(__name__)
    _thinking(bot, update)
    _send_and_log(bot, update, '####### !%s! ########' % welfare_status.shoutout.upper())
    gif_url = random_gif_url(welfare_status.shoutout)
    log.debug(gif_url)
    bot.send_sticker(UpdateRetriever(update).chat_id, gif_url)


def _thinking(bot, update):
    bot.send_chat_action(UpdateRetriever(update).chat_id, 'typing')


def error(bot, update, _error):
    """Log Errors caused by Updates."""
    log.warning('Update "%s" caused error "%s"', update, _error)


class CommandActionHandler(CommandHandler):
    def __init__(self, action, writer_factory, *args, **kwargs):
        """
        :type action: service.action.CommandActionMixin
        :type writer_factory: telegram_service.writer.WriterFactory
        """
        super(CommandActionHandler, self).__init__(action.name, action.command(), *args, **kwargs)
        self.__action = action
        self.writer_factory = writer_factory

    def handle_update(self, update, dispatcher):
        """
        :type update: telegram.Update
        :type dispatcher telegram.ext.Dispatcher
        """
        try:
            return self.callback(self.writer_factory.create(UpdateRetriever(update).chat_id))
        except Exception as e:
            get_logger(__name__).exception(e)
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
        :type action_handler_class: telegram.ext.CommandHandler.__class__
        :type action: service.action.CommandActionMixin
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
