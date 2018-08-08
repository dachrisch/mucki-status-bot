# coding=utf-8
from cachetools.func import ttl_cache

from config import MUCKI_TRACKER_SHEET_ID, MUCKI_TRACKER_TEAM_STATUS_RANGE
from my_logging import get_logger
from sheets import SheetConnector

log = get_logger(__name__)


@ttl_cache()
def per_user_status_details():
    log.info('loading per user status details')
    team_name_status = SheetConnector(MUCKI_TRACKER_SHEET_ID).values_for_range(MUCKI_TRACKER_TEAM_STATUS_RANGE)
    team_name_status_dict = {}
    for user, status, actual, median, trend, rating in team_name_status:
        team_name_status_dict[user] = '%s (%s%s, %s)' % (status, actual, rating, median)
    log.info('done loading welfare status.')
    return team_name_status_dict


@ttl_cache()
def per_user_status_code():
    log.info('loading per user status code')
    team_name_status = SheetConnector(MUCKI_TRACKER_SHEET_ID).values_for_range(MUCKI_TRACKER_TEAM_STATUS_RANGE)
    team_name_status_dict = {}
    for user, status, actual, median, trend, rating in team_name_status:
        team_name_status_dict[user] = status
    log.info('done loading welfare status.')
    return team_name_status_dict


def get_welfare_status_for(name):
    return '%s is %s' % (name, per_user_status_details()[name])
