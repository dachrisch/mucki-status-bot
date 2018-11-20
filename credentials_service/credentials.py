# coding=utf-8
from os import path

from google.oauth2 import service_account

from config import AUTH_FILE, SCOPES


class ServiceAccountCredentialsProvider(object):
    def __init__(self):
        self.service_account_file_path = path.join(path.join(path.expanduser('~'), '.credentials'), AUTH_FILE)
        self.delegate_user = 'cd@it-agile.de'

    def get_credentials(self):
        return service_account.Credentials.from_service_account_file(self.service_account_file_path,
                                                                     scopes=SCOPES).with_subject(self.delegate_user)
