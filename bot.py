# coding=UTF-8
import functools
# https://github.com/eternnoir/pyTelegramBotAPI
import re
import sys
import threading
import time

import schedule
from requests import RequestException
from telebot import TeleBot, types

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
    start_scheduler()
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


def _run_pending():
    while True:
        try:
            if schedule.jobs:
                log.debug('next run in [%d] seconds' % schedule.idle_seconds())
                if schedule.idle_seconds() < 5:
                    globals()['READ_TIMEOUT'] = 3
                    bot.get_me()
                    log.info('about to run next job at %s' % schedule.next_run())
                schedule.run_pending()
            time.sleep(1)
        except RequestException, e:
            log.warn('RequestException during scheduled task: %s', e.message)
            time.sleep(5)


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
    else:
        raise Exception('could not parse time from: %s' % reply_message.text)
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
    bot.reply_to(message, '\n'.join([get_welfare_status_for(name) for name in retrieve_team_status().keys()]))


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
    bot.reply_to(message, '\n'.join(retrieve_team_status().keys()))


def _thinking(message):
    bot.send_chat_action(message.chat.id, 'typing')


def _safe_welfare_lookup(message, name):
    try:
        bot.reply_to(message, get_welfare_status_for(name))
    except KeyError:
        bot.reply_to(message, 'welfare status for %s not found' % name)


main()
