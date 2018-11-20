# coding=utf-8
from googleapiclient import discovery

from credentials_service.credentials import ServiceAccountCredentialsProvider


class GmailConnector(object):
    def __init__(self):
        self.credentials_provider = ServiceAccountCredentialsProvider(scopes=
        (
            'https://www.googleapis.com/auth/gmail.readonly',))

    @property
    def email_count(self):
        service = discovery.build('gmail', 'v1', credentials=self.credentials_provider.get_credentials(delegate=None),
                                  cache_discovery=False)

        results = service.users().messages().list(userId='cd@it-agile.de').execute()
        return results.get('labels', [])


print(GmailConnector().email_count)
