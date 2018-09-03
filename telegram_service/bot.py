# coding=UTF-8
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (CommandHandler, RegexHandler,
                          ConversationHandler, Handler)

from config import MUCKI_TRACKER_SHEET_ID
from google_service.sheets import SheetConnector
from google_service_api.welfare import WelfareStatus
from my_logging import get_logger
from telegram_service.gif import random_gif_url
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


def start(bot, update):
    _send_and_log(bot, update,
                  "I'm the bot of the *Südsterne* team.\n"
                  'I listen for #highlight messages and otherwise offer the following commands:\n'
                  '/howarewe - get status of team\n'
                  '/show_highlights - displays the currently available highlights\n'
                  '/send_highlights - sends highlights to yammer with current week tag\n'
                  '/remote - shows a link to a video chat room for *Südsterne*\n'
                  , is_debug=True)


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


def deals(bot, update):
    _send_and_log(bot, update, 'Alles rosig!')


def remote(bot, update):
    _send_and_log(bot, update, 'Google: https://meet.google.com/upv-baht-nyt\n\n'
                               'Zoom: https://zoom.us/j/6787719716 (log in with Südsterne '
                               'account)\n\n'
                               'Talkyoo: +494095063183 PIN: https://itagile.atlassian.net/wiki/spaces/TIS/pages'
                               '/10486928/Telefonkonferenz > Bezahlter Raum') 


def register_commands(updater):
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('howarewe', howarewe))
    dp.add_handler(RegexHandler(HIGHLIGHTS_PATTERN, collect_highlight))
    dp.add_handler(CommandHandler('show_highlights', show_highlights))
    dp.add_handler(CommandHandler('deals', deals))
    dp.add_handler(CommandHandler('remote', remote))
    dp.add_error_handler(error)
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('send_highlights', ask_for_consent)],
        states={
            1: [RegexHandler('^(yes|no)$', send_highlights)],
        },
        fallbacks=[Handler(cancel)]

    ))


def _send_and_log(bot, update, message, is_debug=False, reply_markup=None):
    global log
    log = get_logger(__name__)
    bot.send_message(UpdateRetriever(update).chat_id, message, reply_markup=reply_markup)
    if is_debug:
        log.debug(message)
    else:
        log.info(message)


def _send_status(bot, update):
    _send_and_log(bot, update, 'calculating welfare status of team...')
    _thinking(bot, update)
    _send_and_log(bot, update, welfare_status.team_message,
                  is_debug=True)


def _send_shoutout(bot, update):
    global log
    _thinking(bot, update)
    _send_and_log(bot, update, '####### !%s! ########' % welfare_status.shoutout.upper(), is_debug=True)
    gif_url = random_gif_url(welfare_status.shoutout)
    log.debug(gif_url)
    bot.send_sticker(UpdateRetriever(update).chat_id, gif_url)


def _thinking(bot, update):
    bot.send_chat_action(UpdateRetriever(update).chat_id, 'typing')


def error(bot, update, _error):
    """Log Errors caused by Updates."""
    log.warning('Update "%s" caused error "%s"', update, _error)
