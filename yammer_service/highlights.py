# coding=UTF-8
import re
from datetime import datetime

from service.action import CommandActionMixin, RegexActionMixin
from yammer_service.yammer import YammerConnector

HIGHLIGHTS = '#highlights'
HIGHLIGHTS_PATTERN = '(?:([^#]*) )?' + HIGHLIGHTS + '(?:[ :]*([^#]*))?'


class Highlights(object):
    def __init__(self):
        self.highlights = {}
        self.__yc = YammerConnector()

    def add(self, username, highlight):
        m = re.match(HIGHLIGHTS_PATTERN, highlight)
        if m:
            self.highlights[username] = (m.group(1) or m.group(2)).strip()
            return True
        else:
            return False

    def get(self, username):
        if username in self.highlights:
            return self.highlights[username]
        else:
            return None

    def is_not_empty(self):
        return not not self.highlights

    def clear(self):
        self.highlights.clear()

    @property
    def message_string(self):
        """

        :rtype: str
        """
        return '\n\n'.join('%s: %s' % (key, val) for (key, val) in self.highlights.items())

    def send_to_yammer(self):
        return self.__yc.post_meine_woche(
            u'Die Südsterne in %s:\n%s' % (current_calendar_week(), self.message_string),
            ('südsterne', current_calendar_week()))


class ShowHighlightsCommandAction(CommandActionMixin):

    def __init__(self, highlights):
        """
        :type highlights: Highlights
        """
        self.highlights = highlights

    def _writer_callback(self, writer):
        if self.highlights.is_not_empty():
            writer.out('the following highlights are available:\n%s' % self.highlights.message_string)
        else:
            writer.out('no highlights available')

    @property
    def name(self):
        return 'show_highlights'

    @property
    def help_text(self):
        return 'Displays currently available highlights'


def current_calendar_week():
    return 'KW_%s' % datetime.today().strftime('%U')


class HighlightsCollectorRegexAction(RegexActionMixin):

    def _writer_callback_with_update(self, update_retriever, writer):
        """
        :type update_retriever: telegram_service.bot.UpdateRetriever
        :type writer: telegram_service.writer.Writer
        """
        self.highlights.add(update_retriever.user, update_retriever.message)
        writer.out(
            'collecting highlight for %s: [%s]' % (update_retriever.user, self.highlights.get(update_retriever.user)))

    @property
    def pattern(self):
        return HIGHLIGHTS_PATTERN

    @property
    def name(self):
        return '#highlights'

    @property
    def help_text(self):
        return 'collects messages with this tag from the current user'

    def __init__(self, highlights):
        self.highlights = highlights
