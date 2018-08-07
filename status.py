# coding=UTF-8

from __future__ import division
from collections import Counter


def calculate_team_rating(status_codes):
    count = Counter(status_codes.values())
    team_rating = count['OK'] / len(status_codes.values())
    return team_rating


def team_rating_to_shoutout(status_codes):
    team_rating = calculate_team_rating(status_codes)

    if team_rating == 1:
        shout = 'perfect'
    elif .75 < team_rating < 1:
        shout = 'awesome'
    elif .625 < team_rating <= .75:
        shout = 'yeah'
    elif .5 < team_rating <= .625:
        shout = 'well'
    elif .375 < team_rating <= .5:
        shout = 'meeehhhh'
    elif .25 < team_rating <= .375:
        shout = 'oh oh'
    elif 0.125 < team_rating <= 0.25:
        shout = 'damn'
    elif 0 < team_rating <= 0.125:
        shout = 'panic'
    else:
        shout = 'freakout'
    return shout
