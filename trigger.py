# coding=UTF-8
import sys

from telebot import TeleBot

from config import MUC_TELEGRAM_GROUP_ID
from sheet import get_welfare_status_for, per_user_status_details


def trigger_howarewe(bot_id):
    bot = TeleBot(bot_id)
    bot.send_message(MUC_TELEGRAM_GROUP_ID,
                     '\n'.join([get_welfare_status_for(name) for name in per_user_status_details().keys()]))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'usage: %s <TOKEN>' % sys.argv[0]
        sys.exit(-1)
    trigger_howarewe(sys.argv[1])
