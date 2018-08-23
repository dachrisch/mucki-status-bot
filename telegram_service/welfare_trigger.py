# coding=UTF-8

import sys

from telegram import Update, Message, Chat
from telegram.ext import Updater

from config import MUC_TELEGRAM_GROUP_ID, CONFIG_PATH
from my_logging import checked_load_logging_config, get_logger
from telegram_service.bot import howarewe


def trigger_howarewe(bot_id):
    updater = Updater(bot_id)
    howarewe(updater.bot, Update(1, Message(1, None, None, Chat(MUC_TELEGRAM_GROUP_ID, 'group'))))


if __name__ == '__main__':
    global log
    checked_load_logging_config(CONFIG_PATH)
    log = get_logger(__name__)
    if len(sys.argv) != 2:
        log.error('usage: %s <TOKEN>' % sys.argv[0])
        sys.exit(-1)
    trigger_howarewe(sys.argv[1])
