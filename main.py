import sys

from telebot import TeleBot

from bot import start_telegram_poll
from my_logging import checked_load_logging_config, basic_logger_config, get_logger


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


if __name__ == '__main__':
    main()
