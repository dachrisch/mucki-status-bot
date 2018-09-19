# coding=utf-8
import os
from collections import Counter
from json import loads

from config import MUCKI_TRACKER_TEAM_STATUS_RANGE
from my_logging import get_logger


class MemberStatus(object):
    def __init__(self, name, status):
        self.name = name
        self.status = status

    @property
    def message(self):
        return '%s is %s' % (self.name, self.status)


class WelfareStatus(object):
    def __init__(self, sheet_connector):
        self.__connector = sheet_connector
        self._log = get_logger(__name__)

    @property
    def team_name_status(self):
        self._log.info('loading team status')
        team_status = loads(self.__connector.values_for_range(MUCKI_TRACKER_TEAM_STATUS_RANGE))
        self._log.info('done loading welfare status.')
        return team_status

    @property
    def team_message(self):
        return '\n'.join([member.message for member in self.team_members])

    @property
    def team_members(self):
        for user, status, actual, median, trend, rating in self.team_name_status:
            yield MemberStatus(user, '%s (%s%s, %s)' % (status, actual, rating, median))

    @property
    def ratings(self):
        for user, status, actual, median, trend, rating in self.team_name_status:
            yield status

    def __calculate_team_rating(self):
        count = Counter(self.ratings)
        # float conversion (fix for python 2)
        team_rating = (0.0 + count['OK']) / len(self.team_name_status)
        return team_rating

    @property
    def shoutout(self):
        team_rating = self.__calculate_team_rating()

        if team_rating == 1:
            shout = os.getenv('SHOUT_PERFECT', 'unicorn dance')
        elif .5 < team_rating < 1:
            shout = os.getenv('SHOUT_AVERAGE', 'well')
        elif 0 < team_rating <= .5:
            shout = os.getenv('SHOUT_BAD', 'crying')
        elif 0 == team_rating:
            shout = os.getenv('SHOUT_PANIC', 'panic scared')
        else:
            shout = 'freakout'
        return shout
