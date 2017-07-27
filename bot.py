import sys
import logging
from sheets import SheetConnector
import telebot
from cachetools.func import ttl_cache

MUCKI_TRACKER_SHEET_ID = '1x5TECCvP3sF3cmMJiD5frkjkmGOVt2pWgNe2eB2zZtI'
MUCKI_TRACKER_TEAM_STATUS_RANGE = 'status!A2:B5'
TOKEN = sys.argv[1]

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)

log.info('starting %s' % __name__)
bot = telebot.TeleBot(TOKEN)


def print_help(message):
    bot.send_message(message.chat.id, 'available commands:\n'
                     '/howami - get status of current user\n'
                     '/howis <name> - get status of specific user\n'
                     '/howarewe - get status of team\n'
                     '/team - get members of team'
                     )


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, 'Hello %s!' % message.from_user.first_name)
    print_help(message)


@bot.message_handler(commands=['howami'])
def howami(message):
    safe_welfare_lookup(message, message.from_user.first_name)


@bot.message_handler(commands=['howarewe'])
def howarewe(message):
    bot.reply_to(message, '\n'.join([get_welfare_status_for(name) for name in retrieve_team_status().keys()]))


@bot.message_handler(commands=['howis'])
def howis(message):
    try:
        command, name = message.text.split(' ')
        safe_welfare_lookup(message, name)
    except ValueError:
        bot.reply_to(message, "can't compile %s. usage: /howis <name>" % message.text)


@bot.message_handler(commands=['team'])
def team(message):
    bot.reply_to(message, '\n'.join(retrieve_team_status().keys()))


def safe_welfare_lookup(message, name):
    try:
        bot.reply_to(message, get_welfare_status_for(name))
    except KeyError:
        bot.reply_to(message, 'welfare status for %s not found' % name)


def get_welfare_status_for(name):
    return 'welfare status of %s is %s' % (name, retrieve_team_status()[name])


@ttl_cache()
def retrieve_team_status():
    log.info('loading welfare status')
    team_name_status = SheetConnector(MUCKI_TRACKER_SHEET_ID).values_for_range(MUCKI_TRACKER_TEAM_STATUS_RANGE)
    team_name_status_dict = {}
    for user, status in team_name_status:
        team_name_status_dict[user] = status
    log.info('done loading welfare status.')
    return team_name_status_dict


log.info('started %s. polling...' % __name__)
bot.polling()
