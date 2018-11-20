# coding=utf-8
import os
from abc import abstractmethod
from os import path

from google.oauth2 import service_account
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from config import AUTH_FILE, SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME
from my_logging import get_logger


class CredentialsProvider(object):
    @abstractmethod
    def get_credentials(self):
        raise NotImplementedError


class ServiceAccountCredentialsProvider(CredentialsProvider):
    def __init__(self, auth_file=AUTH_FILE, scopes=SCOPES):
        self.service_account_file_path = path.join(path.join(path.expanduser('~'), '.credentials'), auth_file)
        self.scopes = scopes

    def get_credentials(self, delegate='cd@it-agile.de'):
        credentials = service_account.Credentials.from_service_account_file(self.service_account_file_path,
                                                                            scopes=self.scopes)
        if delegate:
            credentials = credentials.with_subject(delegate)

        return credentials


class OAuthCredentialsProvider(CredentialsProvider):
    def __init__(self, scopes=SCOPES):
        home_dir = os.path.expanduser('~')
        self.credential_dir = os.path.join(home_dir, '.credentials')
        self.scopes = scopes

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        store = self._get_store()
        credentials = store.get()
        if not credentials or credentials.invalid:
            get_logger(__name__).debug('oauth flow from secret')
            flow = self._flow_from_client_secret()
            flow.user_agent = APPLICATION_NAME
            credentials = tools.run_flow(flow, store)
        return credentials

    def _get_store(self):
        if not os.path.exists(self.credential_dir):
            os.makedirs(self.credential_dir)
        credential_path = os.path.join(self.credential_dir, 'sheets.googleapis.com-python-quickstart.json')
        store = Storage(credential_path)
        return store

    def _flow_from_client_secret(self):
        return client.flow_from_clientsecrets(CLIENT_SECRET_FILE, self.scopes)
