from my_logging import checked_load_logging_config, basic_logger_config, get_logger
from sheet import retrieve_team_status, get_welfare_status_for, retrieve_request_status, get_pretty_request_status

checked_load_logging_config("~/.python/logging.conf")

basic_logger_config()

log = get_logger(__name__)
print '\n'.join([get_welfare_status_for(name) for name in retrieve_team_status().keys()])

print get_pretty_request_status()
