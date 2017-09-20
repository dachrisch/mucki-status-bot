# coding=UTF-8

import logging
import sys

# https://github.com/eternnoir/pyTelegramBotAPI
import telebot
import time
from cachetools.func import ttl_cache
from requests import RequestException

from sheets import SheetConnector

MUCKI_TRACKER_SHEET_ID = '1x5TECCvP3sF3cmMJiD5frkjkmGOVt2pWgNe2eB2zZtI'
MUCKI_TRACKER_TEAM_STATUS_RANGE = 'status!A2:B5'
log = None


def _checked_load_logging_config(config_path):
    from os import path
    import logging.config
    expanded_config_path = path.expanduser(config_path)
    if not path.exists(expanded_config_path):
        raise Exception(
            "failed to locate a logging configuration at [%s]. please check the location" % expanded_config_path)
    logging.config.fileConfig(expanded_config_path)


def startup_bot(arguments):
    global log
    _checked_load_logging_config("~/.python/logging.conf")
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    log = logging.getLogger(__name__)
    log.info('starting %s' % __name__)
    try:
        return telebot.TeleBot(arguments[1])
    except:
        log.error('usage: python %s <TOKEN>', arguments[0])
        sys.exit(255)


bot = startup_bot(sys.argv)


def main():
    log.info('started %s. polling...' % __name__)
    while True:
        try:
            bot.polling()
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
                                      '/howami - get status of current user\n'
                                      '/howis <name> - get status of specific user\n'
                                      '/howarewe - get status of team\n'
                                      '/team - get members of team'
                     )


@bot.message_handler(commands=['howami'])
def howami(message):
    _thinking(message)
    _safe_welfare_lookup(message, message.from_user.first_name)


@bot.message_handler(commands=['howarewe'])
def howarewe(message):
    _thinking(message)
    bot.reply_to(message, '\n'.join([_get_welfare_status_for(name) for name in _retrieve_team_status().keys()]))


@bot.message_handler(commands=['howis'])
def howis(message):
    _thinking(message)
    try:
        command, name = message.text.split(' ')
        _safe_welfare_lookup(message, name)
    except ValueError:
        bot.reply_to(message, "can't compile %s. usage: /howis <name>" % message.text)


@bot.message_handler(commands=['team'])
def team(message):
    _thinking(message)
    bot.reply_to(message, '\n'.join(_retrieve_team_status().keys()))


def _thinking(message):
    bot.send_chat_action(message.chat.id, 'typing')


def _safe_welfare_lookup(message, name):
    try:
        bot.reply_to(message, _get_welfare_status_for(name))
    except KeyError:
        bot.reply_to(message, 'welfare status for %s not found' % name)


def _get_welfare_status_for(name):
    return 'welfare status of %s is %s' % (name, _retrieve_team_status()[name])


@ttl_cache()
def _retrieve_team_status():
    log.info('loading welfare status')
    team_name_status = SheetConnector(MUCKI_TRACKER_SHEET_ID).values_for_range(MUCKI_TRACKER_TEAM_STATUS_RANGE)
    team_name_status_dict = {}
    for user, status in team_name_status:
        team_name_status_dict[user] = status
    log.info('done loading welfare status.')
    return team_name_status_dict


main()
