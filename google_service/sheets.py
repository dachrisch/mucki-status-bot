# coding=utf-8

from apiclient import discovery
from cachetools import TTLCache

from credentials_service.credentials import ServiceAccountCredentialsProvider
from my_logging import get_logger


def key(sheet_id, sheet_range):
    return sheet_id + sheet_range


class SheetConnector(TTLCache):
    def __init__(self, sheet_id):
        TTLCache.__init__(self, maxsize=128, ttl=600)
        self.__sheet_id = sheet_id
        self.credentials_provider = ServiceAccountCredentialsProvider()

    def values_for_range(self, sheet_range):
        values = None
        try:
            values = self[key(self.__sheet_id, sheet_range)]
            get_logger(__name__).debug('using cached values')
        except KeyError:
            get_logger(__name__).debug('invocation not cached')

        if not values:
            service = discovery.build('sheets', 'v4', credentials=self.credentials_provider.get_credentials(),
                                      cache_discovery=False)
            values = service.spreadsheets().values().get(spreadsheetId=self.__sheet_id,
                                                         range=sheet_range).execute().get('values', [])
            self[key(self.__sheet_id, sheet_range)] = values
        return values
