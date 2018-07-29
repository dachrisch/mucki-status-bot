from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
import os

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
from config import APPLICATION_NAME, CLIENT_SECRET_FILE, SCOPES
from my_logging import get_logger


class SheetConnector(object):
    def __init__(self, sheet_id):
        self.__sheet_id = sheet_id
        self.__service = discovery.build('sheets', 'v4', credentials=self.get_credentials())

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
        store = Storage(credential_path)
        return store

    @classmethod
    def _client_id(cls):
        return os.environ.get('CLIENT_ID')

    @classmethod
    def _client_secret(cls):
        return os.environ.get('CLIENT_SECRET')

    @classmethod
    def flow(cls, client_id, client_secret, redirect_uri):
        return OAuth2WebServerFlow(client_id, client_secret, SCOPES, redirect_uri)

    @classmethod
    def flow_from_env(cls, redirect_uri):
        return OAuth2WebServerFlow(cls._client_id(), cls._client_secret(), SCOPES, redirect_uri)

    @classmethod
    def _flow_from_client_secret(cls):
        return client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)

    def values_for_range(self, sheet_range):
        return self.__service.spreadsheets().values().get(spreadsheetId=self.__sheet_id,
                                                          range=sheet_range).execute().get('values', [])

    @classmethod
    def store(cls, credentials):
        store = cls._get_store()
        store.put(credentials)
