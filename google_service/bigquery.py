# coding=utf-8
from abc import abstractmethod
from os import path

from google.cloud import bigquery
from google.oauth2 import service_account

AVERAGE_MESSAGES_QUERY = """
SELECT
  AVG(Inbox_Thread_Count) AS average
FROM
  `suedsterne-1328.inbox_zero.message_ages`
WHERE
  CAST(Date_Checked AS datetime) > DATETIME_sub(CURRENT_DATETIME(),
    INTERVAL @days day)
  AND mate = @mate
"""
QUARTILE_QUERY = """
SELECT
  QUANTILES(Inbox_Thread_Count, 5) AS quartile
FROM
  inbox_zero.message_ages
WHERE
  Date_Checked > DATE_ADD(CURRENT_TIMESTAMP(), -%d, "Day")
  AND mate = '%s'
"""


class BigQueryClientWrapper(object):
    @abstractmethod
    def query(self, *args, **kwargs):
        raise NotImplementedError


class SuedSterneBigQueryClientWrapper(BigQueryClientWrapper):
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            path.join(path.join(path.expanduser('~'), '.credentials'), 'suedsterne-1328.json'),
            scopes=bigquery.Client.SCOPE).with_subject('cd@it-agile.de')
        self.bigquery_client = bigquery.Client('suedsterne-1328', credentials)

    def query(self, *args, **kwargs):
        return self.bigquery_client.query(*args, **kwargs)


class NoValuesFoundException(Exception):
    pass


class InboxZeroBigQueryConnector(object):
    def __init__(self, bigquery_client):
        """
        :type bigquery_client: google_service.bigquery.BigQueryClientWrapper
        """
        self.bigquery_client = bigquery_client

    def average_inbox_count(self, mate, days=3):
        job_config = bigquery.QueryJobConfig()
        job_config.query_parameters = (
            bigquery.ScalarQueryParameter('mate', 'STRING', mate),
            bigquery.ScalarQueryParameter('days', 'INT64', days)
        )
        results = self.bigquery_client.query(AVERAGE_MESSAGES_QUERY, job_config=job_config).result()
        result_list = [row.average for row in results]
        if len(result_list) == 1:
            return result_list[0]
        elif len(result_list) == 0:
            raise NoValuesFoundException('Query returned no results for mate [%s]' % mate)
        else:
            raise Exception('More than one result returned...something is wrong with the query.')

    def quartile(self, mate, days, quartile_num):
        job_config = bigquery.QueryJobConfig()
        job_config.use_legacy_sql = True
        query_job = self.bigquery_client.query(QUARTILE_QUERY % (days, mate), job_config=job_config)
        results = query_job.result()
        result_list = [row.quartile for row in results]
        if len(result_list) == 5:
            return result_list[quartile_num]
        elif len(result_list) == 0:
            raise NoValuesFoundException('Query returned no results for mate [%s]' % mate)
        else:
            raise Exception('More than one result returned...something is wrong with the query.')
