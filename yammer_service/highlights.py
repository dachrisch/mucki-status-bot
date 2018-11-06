# coding=UTF-8
import re
from datetime import datetime

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from service.action import CommandActionMixin, RegexActionMixin, ConversationActionMixin
from yammer_service.yammer import YammerConnector

HIGHLIGHTS = '#highlights'
HIGHLIGHTS_PATTERN = '(?:([^#]*) )?' + HIGHLIGHTS + '(?:[ :]*([^#]*))?'


class Highlights(object):
    def __init__(self):
        self.highlights = {}
        self.yc = YammerConnector()

    def add_pattern(self, username, highlight):
        m = re.match(HIGHLIGHTS_PATTERN, highlight)
        if m:
            self.add(username, (m.group(1) or m.group(2)).strip())
            return True
        else:
            return False

    def add(self, username, text):
        self.highlights[username] = text

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
        return self.yc.post_meine_woche(
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
            writer.out('the following highlights are available:\n%s\n' % self.highlights.message_string)
        else:
            writer.out('no highlights available')

    @property
    def name(self):
        return 'show_highlights'

    @property
    def help_text(self):
        return 'Displays currently available highlights'


def current_calendar_week():
    return 'KW_%s' % datetime.today().strftime('%V')


class HighlightsCollectorRegexAction(RegexActionMixin):

    def __init__(self, highlights):
        self.highlights = highlights

    def _writer_callback_with_update(self, update_retriever, writer):
        """
        :type update_retriever: telegram_service.retriever.UpdateRetriever
        :type writer: telegram_service.writer.Writer
        """
        user = update_retriever.user
        message = update_retriever.message
        self.highlights.add_pattern(user, message)
        writer.out(
            'collecting highlight for %s: [%s]' % (user, self.highlights.get(user)))

    @property
    def pattern(self):
        return HIGHLIGHTS_PATTERN

    @property
    def name(self):
        return '#highlights'

    @property
    def help_text(self):
        return 'collects messages with this tag from the current user'


class AskForHighlightsConsentCommandAction(CommandActionMixin):

    def __init__(self, highlights, pre_command_action):
        """
        :type highlights: Highlights
        :type pre_command_action: service.action.CommandActionMixin
        """
        self.highlights = highlights
        self.pre_command_action = pre_command_action

    def _writer_callback(self, writer):
        self.pre_command_action.callback_function(writer)
        reply_keyboard = [['yes', 'no']]
        if self.highlights.is_not_empty():
            writer.out('really send?\n',
                       reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            return 1
        else:
            return ConversationHandler.END

    @property
    def name(self):
        return 'send_highlights'

    @property
    def help_text(self):
        return 'Displays currently available highlights'


class SendHighlightsCommandAction(RegexActionMixin):

    def __init__(self, highlights):
        self.highlights = highlights

    @property
    def pattern(self):
        return '^(yes|no)$'

    def _writer_callback_with_update(self, update_retriever, writer):
        if update_retriever.message == 'yes':
            try:
                message_url = self.highlights.send_to_yammer()
                writer.out('highlights posted to yammer: [%s]' % message_url,
                           reply_markup=ReplyKeyboardRemove())
            except Exception as e:
                writer.out('failed to post to yammer: [%s]' % e, reply_markup=ReplyKeyboardRemove())

            self.highlights.clear()
        else:
            self.cancel(writer)
        return ConversationHandler.END

    @property
    def name(self):
        return 'send_highlights'

    @property
    def help_text(self):
        pass

    def cancel(self, writer):
        writer.out('ok, not sending highlights.', reply_markup=ReplyKeyboardRemove())


class SendHighlightsConversationAction(ConversationActionMixin):
    def __init__(self, highlights, expected_member):
        """
        :type highlights: yammer_service.highlights.Highlights
        :type expected_member: [str]
        """
        self.highlights = highlights
        self.expected_member = expected_member

    @property
    def name(self):
        return 'send_highlights'

    @property
    def help_text(self):
        return 'Posts current #highlights to Yammer' + \
               '@ https://www.yammer.com/it-agile.de/#/threads/inGroup?type=in_group&feedId=207628'

    @property
    def yes_callback(self):
        return SendHighlightsCommandAction(self.highlights)

    @property
    def entry_action(self):
        return AskForHighlightsConsentCommandAction(self.highlights,
                                                    CheckHighlightsCommandAction(self.highlights, self.expected_member))

    @property
    def no_callback(self):
        pass


class CheckHighlightsCommandAction(CommandActionMixin):

    def __init__(self, highlights, expected_member):
        """
        :type highlights: yammer_service.highlights.Highlights
        :type expected_member: [str]
        """
        self.highlights = highlights
        self.expected_member = expected_member

    def _writer_callback(self, writer):
        diff = list(filter(lambda user: not self.highlights.get(user), self.expected_member))
        if diff:
            writer.out('No highlights available for: [%s]\n' % ', '.join(['%s' % member for member in diff]))
        else:
            writer.out('All members have highlights \o/\n')

    @property
    def name(self):
        return 'check_highlights'

    @property
    def help_text(self):
        return 'Checks all members have highlights'


class HighlightsForCommandAction(CommandActionMixin):
    def __init__(self, highlights):
        self.highlights = highlights
        self.collector_action = HighlightsCollectorRegexAction(self.highlights)

    def _writer_callback(self, writer, message=None):
        if message and len(message.split(' ')) > 2:
            user, *text = message.split(' ')[1:]
            message = ' '.join(text)
            self.highlights.add(user, message)
            writer.out(
                'collecting highlight for %s: [%s]' % (user, self.highlights.get(user)))
        else:
            writer.out(self.usage)

    @property
    def usage(self):
        return 'Usage: /%s <user> <highlight>' % self.name

    @property
    def name(self):
        return 'highlights_for'

    @property
    def help_text(self):
        return 'Collects highlights for a specific user (%s)' % self.usage
