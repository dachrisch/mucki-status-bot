# coding=utf-8
from config import MUCKI_TRACKER_SHEET_ID
from google_service.sheets import SheetConnector
from google_service_api.welfare import WelfareStatus
from my_logging import checked_load_logging_config, get_logger
from telegram_service.gif import random_gif_url

checked_load_logging_config("~/.python/logging_debug.conf")

log = get_logger(__name__)
welfare_status = WelfareStatus(SheetConnector(MUCKI_TRACKER_SHEET_ID))
print(welfare_status.team_message)
print(welfare_status.shoutout)
print(random_gif_url(welfare_status.shoutout))
