# coding=utf-8
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
from config import APPLICATION_NAME, CLIENT_SECRET_FILE, SCOPES
from my_logging import get_logger
from json import dumps


class _SymlinkAwareStorage(Storage):
    def __init__(self, *args, **kwargs):
        Storage.__init__(self, *args, **kwargs)
        self.__credentials = self.__read_from_file()

    def locked_get(self):
        return self.__credentials

    def __read_from_file(self):
        f = open(self._filename, 'rb')
        content = f.read()
        f.close()
        credentials = client.Credentials.new_from_json(content)
        credentials.set_store(self)

        return credentials

    def locked_put(self, credentials):
        get_logger(__name__).warning(
            'ignoring credentials update for [%(user_agent)s] which expired %(token_expiry)s' % credentials.__dict__)


class SheetConnector(object):
    def __init__(self, sheet_id):
        self.__sheet_id = sheet_id

    @classmethod
    def get_credentials(cls):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        store = cls._get_store()
        credentials = store.get()
        if not credentials or credentials.invalid:
            get_logger(__name__).debug('oauth flow from secret')
            flow = cls._flow_from_client_secret()
            flow.user_agent = APPLICATION_NAME
            credentials = tools.run_flow(flow, store)
        return credentials

    @classmethod
    def _get_store(cls):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'sheets.googleapis.com-python-quickstart.json')
        store = _SymlinkAwareStorage(credential_path)
        return store

    @classmethod
    def _flow_from_client_secret(cls):
        return client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)

    def values_for_range(self, sheet_range):
        service = discovery.build('sheets', 'v4', credentials=self.get_credentials())
        return dumps(service.spreadsheets().values().get(spreadsheetId=self.__sheet_id,
                                                         range=sheet_range).execute().get('values', []))
