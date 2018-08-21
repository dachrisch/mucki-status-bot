# coding=UTF-8

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (CommandHandler, RegexHandler,
                          ConversationHandler, Handler)

from google_service_api.sheet import per_user_status_details, get_welfare_status_for, per_user_status_code
from my_logging import get_logger
from telegram_service.gif import random_gif_url
from telegram_service.status import team_rating_to_shoutout
from yammer_service.highlights import Highlights, HIGHLIGHTS_PATTERN

log = None
highlights = Highlights()


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


def register_commands(updater):
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('howarewe', howarewe))
    dp.add_handler(RegexHandler(HIGHLIGHTS_PATTERN, collect_highlight))
    dp.add_handler(CommandHandler('show_highlights', show_highlights))
    dp.add_handler(CommandHandler('deals', deals))
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
    _send_and_log(bot, update, '\n'.join([get_welfare_status_for(name) for name in per_user_status_details().keys()]),
                  is_debug=True)


def _send_shoutout(bot, update):
    global log
    _thinking(bot, update)
    shoutout = team_rating_to_shoutout(per_user_status_code())
    _send_and_log(bot, update, '####### !%s! ########' % shoutout.upper(), is_debug=True)
    gif_url = random_gif_url(shoutout)
    log.debug(gif_url)
    bot.send_sticker(UpdateRetriever(update).chat_id, gif_url)


def _thinking(bot, update):
    bot.send_chat_action(UpdateRetriever(update).chat_id, 'typing')


def error(bot, update, _error):
    """Log Errors caused by Updates."""
    log.warning('Update "%s" caused error "%s"', update, _error)