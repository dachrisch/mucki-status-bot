from cachetools.func import ttl_cache

from my_logging import get_logger
from sheets import SheetConnector

MUCKI_TRACKER_SHEET_ID = '1x5TECCvP3sF3cmMJiD5frkjkmGOVt2pWgNe2eB2zZtI'
MUCKI_TRACKER_TEAM_STATUS_RANGE = 'status!A2:F5'

PIPEDRIVE_TRACKER_SHEET_ID = '1pdiUyvbSKEwcx7jowtcV6Z48Uyu5dtthtchy9GFVX7I'
PIPEDRIVE_TRACKER_RANGE = 'CU!B2:B3'

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


@ttl_cache()
def retrieve_request_status():
    log.info('loading request status')
    request_status = SheetConnector(PIPEDRIVE_TRACKER_SHEET_ID).values_for_range(PIPEDRIVE_TRACKER_RANGE)
    assert len(request_status) == 2
    request_status_dict = {'expected deals': int(request_status[0][0]), 'actual deals': int(request_status[1][0])}
    log.info('done loading request status.')
    return request_status_dict


def get_pretty_request_status():
    request_status_dict = retrieve_request_status()
    if request_status_dict['actual deals'] >= request_status_dict['expected deals']:
        return 'deals are OK (%d>=%d)' % (
            request_status_dict['actual deals'], request_status_dict['expected deals'])
    else:
        return 'deals are zu wenig (%d<%d)' % (
            request_status_dict['actual deals'], request_status_dict['expected deals'])
