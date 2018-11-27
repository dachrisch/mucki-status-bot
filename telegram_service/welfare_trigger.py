# coding=UTF-8
import os
import sys

from telegram.ext import Updater

from config import MUC_TELEGRAM_GROUP_ID, CONFIG_PATH, BOT_TOKEN
from google_service_api.welfare import WelfareCommandAction
from my_logging import checked_load_logging_config, get_logger
from telegram_service.writer import TelegramWriter


def trigger_howarewe(token):
    global log
    checked_load_logging_config(CONFIG_PATH)

    log = get_logger(__name__)
    if not token:
        log.error('usage: %s=<token> python %s' % (BOT_TOKEN, os.path.basename(__file__)))
        sys.exit(255)
    log.info('starting %s' % __name__)
    updater = Updater(token)

    writer = TelegramWriter(updater.bot, MUC_TELEGRAM_GROUP_ID)
    WelfareCommandAction().callback_function(writer)


if __name__ == '__main__':
    trigger_howarewe(os.getenv(BOT_TOKEN))
