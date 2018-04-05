from cachetools.func import ttl_cache

from my_logging import get_logger
from sheets import SheetConnector

MUCKI_TRACKER_SHEET_ID = '1x5TECCvP3sF3cmMJiD5frkjkmGOVt2pWgNe2eB2zZtI'
MUCKI_TRACKER_TEAM_STATUS_RANGE = 'status!A2:F6'

log = get_logger(__name__)


@ttl_cache()
def retrieve_team_status():
    log.info('loading welfare status')
    team_name_status = SheetConnector(MUCKI_TRACKER_SHEET_ID).values_for_range(MUCKI_TRACKER_TEAM_STATUS_RANGE)
    team_name_status_dict = {}
    for user, status, actual, median, trend, rating in team_name_status:
        team_name_status_dict[user] = '%s (%s%s, %s)' % (status, actual, rating, median)
    log.info('done loading welfare status.')
    return team_name_status_dict


def get_welfare_status_for(name):
    return '%s is %s' % (name, retrieve_team_status()[name])
