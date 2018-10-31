# coding=utf-8
from google_service_api.welfare import WelfareCommandAction
from my_logging import checked_load_logging_config, get_logger
from tests.telegram_test_bot import LoggingWriter

checked_load_logging_config("~/.python/logging_debug.conf")

log = get_logger(__name__)
action = WelfareCommandAction()
writer = LoggingWriter()
action._writer_callback(writer)

print(writer.message)
