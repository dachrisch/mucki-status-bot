# coding=UTF-8
import functools
import logging
# https://github.com/eternnoir/pyTelegramBotAPI
import re
import sys
import threading
import time

import schedule
from cachetools.func import ttl_cache
from requests import RequestException
from telebot import TeleBot, types

from sheets import SheetConnector

MUCKI_TRACKER_SHEET_ID = '1x5TECCvP3sF3cmMJiD5frkjkmGOVt2pWgNe2eB2zZtI'
MUCKI_TRACKER_TEAM_STATUS_RANGE = 'status!A2:F5'
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
        return TeleBot(arguments[1])
    except:
        log.error('usage: python %s <TOKEN>', arguments[0])
        sys.exit(255)


bot = startup_bot(sys.argv)


def main():
    log.info('started %s. polling...' % __name__)
    start_scheduler()
    start_telegram_poll()


def start_telegram_poll():
    while True:
        try:
            bot.polling()
            break
        except RequestException, e:
            log.warn('restarting after RequestException: %s', e.message)
            bot.stop_polling()
            time.sleep(5)


def _run_pending():
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler():
    th = threading.Thread(target=_run_pending)
    th.daemon = True
    th.start()


def _schedule_from_reply(reply_message):
    try:
        parsed_time = _parse_time(reply_message)
        _schedule_message_reply(parsed_time, reply_message)
    except ValueError, ve:
        bot.send_message(reply_message.chat.id, 'time not in format [HH:MM]')
        log.error(ve)


def _parse_time(reply_message):
    if re.search('\d:\d', reply_message.text):
        parsed_time = time.strptime(reply_message.text, '%H:%M')
    elif re.search('\d{3,4}', reply_message.text):
        parsed_time = time.strptime(reply_message.text, '%H%M')
    elif re.search('\d{2}', reply_message.text):
        parsed_time = time.strptime(reply_message.text, '%H')
    return parsed_time


def _schedule_message_reply(parsed_time, reply_message):
    schedule.clear()
    scheduled_time = '%02d:%02d' % (parsed_time.tm_hour, parsed_time.tm_min)
    scheduled_message = bot.send_message(reply_message.chat.id,
                                         'scheduling bot for [%s] every day' % scheduled_time)
    schedule.every().day.at(scheduled_time).do(functools.partial(howarewe, scheduled_message))


@bot.message_handler(commands=['schedule'])
def schedule_command(message):
    reply_to_message = bot.send_message(message.chat.id, 'Schedule for which time [HH:MM]: ',
                                        reply_markup=types.ForceReply())
    bot.register_for_reply(reply_to_message, _schedule_from_reply)


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
                                      '/team - get members of team\n'
                                      '/schedule - schedule a /howarewe command every day at specified time'
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
    return '%s is %s' % (name, _retrieve_team_status()[name])


@ttl_cache()
def _retrieve_team_status():
    log.info('loading welfare status')
    team_name_status = SheetConnector(MUCKI_TRACKER_SHEET_ID).values_for_range(MUCKI_TRACKER_TEAM_STATUS_RANGE)
    team_name_status_dict = {}
    for user, status, actual, median, trend, rating in team_name_status:
        team_name_status_dict[user] = '%s (%s, %s)' % (status, actual, median)
    log.info('done loading welfare status.')
    return team_name_status_dict


main()
