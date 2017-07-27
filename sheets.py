from oauth2client.file import Storage
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
import os

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Muckibot'


class SheetConnector(object):
    def __init__(self, sheet_id):
        self.__sheet_id = sheet_id
        self.__service = discovery.build('sheets', 'v4', credentials=self._get_credentials())

    @classmethod
    def _get_credentials(cls):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'sheets.googleapis.com-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            credentials = tools.run_flow(flow, store)
        return credentials

    def values_for_range(self, sheet_range):
        return self.__service.spreadsheets().values().get(spreadsheetId=self.__sheet_id,
                                                          range=sheet_range).execute().get('values', [])
