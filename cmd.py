from my_logging import checked_load_logging_config, basic_logger_config, get_logger
from sheet import retrieve_team_status, get_welfare_status_for

checked_load_logging_config("~/.python/logging_debug.conf")

log = get_logger(__name__)
print '\n'.join([get_welfare_status_for(name) for name in retrieve_team_status().keys()])

