# coding=UTF-8
# https://github.com/eternnoir/pyTelegramBotAPI
import sys
import time

from requests import RequestException
from telebot import TeleBot

from my_logging import checked_load_logging_config, basic_logger_config, get_logger
from sheet import retrieve_team_status, get_welfare_status_for

log = None


def startup_bot(arguments):
    global log
    checked_load_logging_config("~/.python/logging.conf")

    basic_logger_config()

    log = get_logger(__name__)
    log.info('starting %s' % __name__)
    try:
        return TeleBot(arguments[1])
    except:
        log.error('usage: python %s <TOKEN>', arguments[0])
        sys.exit(255)


bot = startup_bot(sys.argv)


def main():
    start_telegram_poll()


def start_telegram_poll():
    while True:
        try:
            log.info('started %s. polling...' % __name__)
            bot.polling()
            log.info('finished polling')
            break
        except RequestException, e:
            log.warn('restarting after RequestException: %s', e.message)
            bot.stop_polling()
            time.sleep(5)


@bot.message_handler(commands=['start', ])
def start(message):
    bot.reply_to(message, 'Hello %s!' % message.from_user.first_name)
    print_help(message)


@bot.message_handler(commands=['start', 'help'])
def print_help(message):
    bot.send_message(message.chat.id, 'available commands:\n'
                                      '/howarewe - get status of team\n'
                     )


@bot.message_handler(commands=['howarewe'])
def howarewe(message):
    _thinking(message)
    bot.reply_to(message, '\n'.join([get_welfare_status_for(name) for name in retrieve_team_status().keys()]))


def _thinking(message):
    bot.send_chat_action(message.chat.id, 'typing')


main()
