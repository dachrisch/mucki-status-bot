# coding=utf-8
import os

import requests

from config import PIPEDRIVE_API_TOKEN, PIPEDRIVE_FILTER_ID, PIPEDRIVE_PIPLINE_ID, PIPEDRIVE_URL, \
    PIPEDRIVE_COUNT_STAGES_FILTER, PIPEDRIVE_VALUE_STAGES_FILTER, TEAM_MATES_COUNT, PIPEDRIVE_MIN_DEALS_PER_MATE, \
    PIPEDRIVE_MIN_EUROS_PER_MATE
from my_logging import get_logger, checked_load_logging_config

log = get_logger(__name__)

PIPEDRIVE_REQUEST_API_TOKEN = '&api_token=' + os.getenv(PIPEDRIVE_API_TOKEN, '')


def ask_pipedrive():
    global log
    stages = get_stages()

    value_sum = 0
    deal_count = 0
    for stage in stages:
        if stage['name'] in PIPEDRIVE_VALUE_STAGES_FILTER:
            value_sum += sum_of_deal_values(stage)
        if stage['name'] in PIPEDRIVE_COUNT_STAGES_FILTER:
            deal_count += len(get_deals(stage['id']))

    return get_interpretation(deal_count, value_sum)


def get_interpretation(deal_count, value_sum):
    data = {'value_sum': value_sum, 'deal_count': deal_count}
    money = {'enough_money': have_enough_money(value_sum), 'difference': money_difference(value_sum)}
    deals = {'enough_deals': have_enough_deals(deal_count), 'difference': deals_difference(deal_count)}
    interpretation = {'money': money, 'deals': deals}
    return {'data': data, 'interpretation': interpretation}


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
                    + str(stage_id) + '&status=all_not_deleted&start=0' + PIPEDRIVE_REQUEST_API_TOKEN
    stage_response = get_response(stage_request)
    deals = stage_response.json()['data']
    return deals


def get_stages():
    stages_request = PIPEDRIVE_URL + 'stages?pipeline_id=' + PIPEDRIVE_PIPLINE_ID + PIPEDRIVE_REQUEST_API_TOKEN
    stages_response = get_response(stages_request)
    stages = stages_response.json()['data']
    return stages


def get_response(url):
    response = requests.get(url)
    if response.status_code != 200:
        log.error('Request faild: ' + url)
        log.error(response.json())
    return response


def have_enough_money(value_sum):
    return (value_sum/TEAM_MATES_COUNT) >= PIPEDRIVE_MIN_EUROS_PER_MATE


def have_enough_deals(deal_count):
    return (deal_count/TEAM_MATES_COUNT) >= PIPEDRIVE_MIN_DEALS_PER_MATE


def money_difference(value_sum):
    return value_sum - PIPEDRIVE_MIN_EUROS_PER_MATE * TEAM_MATES_COUNT


def deals_difference(deal_count):
    return deal_count - PIPEDRIVE_MIN_DEALS_PER_MATE * TEAM_MATES_COUNT


if __name__ == '__main__':
    checked_load_logging_config("~/.python/logging_debug.conf")
    log = get_logger(__name__)
    log.info(ask_pipedrive())
