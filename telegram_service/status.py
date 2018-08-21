# coding=UTF-8

import os
from collections import Counter


def calculate_team_rating(status_codes):
    count = Counter(status_codes.values())
    team_rating = count['OK'] / len(status_codes.values())
    return team_rating


def team_rating_to_shoutout(status_codes):
    team_rating = calculate_team_rating(status_codes)

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
