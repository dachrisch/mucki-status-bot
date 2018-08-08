from __future__ import print_function

from my_logging import checked_load_logging_config, get_logger
from sheet import per_user_status_details, get_welfare_status_for

checked_load_logging_config("~/.python/logging_debug.conf")

log = get_logger(__name__)
print('\n'.join([get_welfare_status_for(name) for name in per_user_status_details().keys()]))

