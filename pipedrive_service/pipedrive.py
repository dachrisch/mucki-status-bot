import requests

from my_logging import get_logger
from config import PIPEDRIVE_API_TOKEN, PIPEDRIVE_FILTER_ID, PIPEDRIVE_PIPLINE_ID, PIPEDRIVE_URL, \
    PIPEDRIVE_COUNT_STAGES_FILTER, PIPEDRIVE_VALUE_STAGES_FILTER

log = get_logger(__name__)


def ask_pipedrive():
    stages = get_stages()

    value_sum = 0
    deal_count = 0
    for stage in stages:
        if stage['name'] in PIPEDRIVE_VALUE_STAGES_FILTER:
            value_sum += sum_of_deal_values(stage)
        if stage['name'] in PIPEDRIVE_COUNT_STAGES_FILTER:
            deal_count += len(get_deals(stage['id']))
    log.info(value_sum)
    log.info(deal_count)


def sum_of_deal_values(stage):
    deals = get_deals(stage['id'])
    return sum_of_values(deals)


def sum_of_values(deals):
    deals_value_sum = 0
    for deal in deals:
        deals_value_sum += deal['value']
    return deals_value_sum


def get_deals(stage_id):
    stage_request = PIPEDRIVE_URL + 'deals?filter_id=' + PIPEDRIVE_FILTER_ID + '&stage_id=' \
                    + str(stage_id) + '&status=all_not_deleted&start=0' + PIPEDRIVE_API_TOKEN
    stage_response = get_response(stage_request)
    deals = stage_response.json()['data']
    return deals


def get_stages():
    stages_request = PIPEDRIVE_URL + 'stages?pipeline_id=' + PIPEDRIVE_PIPLINE_ID + PIPEDRIVE_API_TOKEN
    stages_response = get_response(stages_request)
    stages = stages_response.json()['data']
    return stages


def get_response(url):
    response = requests.get(url)
    if response.status_code != 200:
        log.error('Request faild: ' + url)
        log.error(response.json())
    return response
