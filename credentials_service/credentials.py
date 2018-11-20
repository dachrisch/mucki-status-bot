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
    def __init__(self):
        self.service_account_file_path = path.join(path.join(path.expanduser('~'), '.credentials'), AUTH_FILE)
        self.delegate_user = 'cd@it-agile.de'

    def get_credentials(self):
        return service_account.Credentials.from_service_account_file(self.service_account_file_path,
                                                                     scopes=SCOPES).with_subject(self.delegate_user)


class OAuthCredentialsProvider(CredentialsProvider):
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

    def __init__(self):
        home_dir = os.path.expanduser('~')
        self.credential_dir = os.path.join(home_dir, '.credentials')

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
        store = OAuthCredentialsProvider._SymlinkAwareStorage(credential_path)
        return store

    def _flow_from_client_secret(self):
        return client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
