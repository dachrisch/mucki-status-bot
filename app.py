# coding=utf-8
import os
import sys

from telegram.ext import Updater

from config import BOT_TOKEN, CONFIG_PATH
from my_logging import checked_load_logging_config, get_logger
from telegram_service.bot import BotRegistry


def main():
    _startup_bot(os.getenv(BOT_TOKEN))


def _startup_bot(token):
    global log
    checked_load_logging_config(CONFIG_PATH)

    log = get_logger(__name__)
    if not token:
        log.error('usage: %s=<token> python %s' % (BOT_TOKEN, os.path.basename(__file__)))
        sys.exit(255)
    log.info('starting %s' % __name__)
    updater = Updater(token)
    BotRegistry(updater).register_commands()
    updater.start_polling()
    updater.idle()
    log.info('finished polling')


if __name__ == '__main__':
    main()
