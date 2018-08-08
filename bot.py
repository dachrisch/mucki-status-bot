# coding=UTF-8
import os
import sys

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, RegexHandler,
                          ConversationHandler, Handler)

from config import WITH_WEB, BOT_TOKEN, CONFIG_PATH
from gif import random_gif_url
from highlights import Highlights, HIGHLIGHTS_PATTERN
from my_logging import checked_load_logging_config, get_logger
from sheet import per_user_status_details, get_welfare_status_for, per_user_status_code
from status import team_rating_to_shoutout
from web import start_server, kill_server

log = None
highlights = Highlights()


def _startup_bot(token):
    global log
    checked_load_logging_config(CONFIG_PATH)

    log = get_logger(__name__)
    if not token:
        log.error('usage: %s=<token> python %s' % (BOT_TOKEN, os.path.basename(__file__)))
        sys.exit(255)
    log.info('starting %s' % __name__)
    updater = Updater(token)
    _register_commands(updater)
    updater.start_polling()
    updater.idle()
    log.info('finished polling')


def main():
    try:
        if os.getenv(WITH_WEB):
            start_server()
        _startup_bot(os.getenv(BOT_TOKEN))
    finally:
        if os.getenv(WITH_WEB):
            kill_server()


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
        _send_and_log(bot, update, 'failed to obtain status: [%s]' % e.message)


def collect_highlight(bot, update):
    user = UpdateRetriever(update).user
    if highlights.add(user, unicode(update.message.text)):
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
            _send_and_log(bot, update, 'failed to post to yammer: [%s]' % e.message, reply_markup=ReplyKeyboardRemove())

        highlights.clear()
    else:
        cancel(bot, update)
    return ConversationHandler.END


def cancel(bot, update):
    _send_and_log(bot, update, 'ok, not sending highlights.', reply_markup=ReplyKeyboardRemove())


def _register_commands(updater):
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
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


if __name__ == '__main__':
    main()
