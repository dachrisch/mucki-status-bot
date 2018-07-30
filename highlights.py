# coding=UTF-8
import re
from datetime import datetime

from yammer import YammerConnector

HIGHLIGHTS_PATTERN = '#highlights[ :]+'


class Highlights(object):
    def __init__(self):
        self.__highlights = {}
        self.__yc = YammerConnector()

    def add(self, username, highlight):
        text = re.sub(HIGHLIGHTS_PATTERN, '', highlight).strip()
        if text:
            self.__highlights[username] = text
            return True
        else:
            return False

    def get(self, username):
        if self.__highlights.has_key(username):
            return self.__highlights[username]
        else:
            return None

    def is_not_empty(self):
        return not not self.__highlights

    def clear(self):
        self.__highlights.clear()

    def message_string(self):
        return '\n'.join('%s: %s' % (key, val) for (key, val) in self.__highlights.iteritems())

    def send_to_yammer(self):
        return self.__yc.post_meine_woche(u'Die Südsterne in %s:\n%s' % (current_calendar_week(), self.message_string()),
                                          ('südsterne', current_calendar_week()))


def current_calendar_week():
    return 'KW_%s' % datetime.today().strftime('%U')
