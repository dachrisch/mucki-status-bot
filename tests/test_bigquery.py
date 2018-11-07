# coding=utf-8
import unittest

from google.cloud.bigquery import DEFAULT_RETRY, QueryJob
from google.cloud.bigquery.table import RowIterator

from google_service.bigquery import InboxZeroBigQueryConnector, BigQueryClientWrapper, SuedSterneBigQueryClientWrapper, \
    NoValuesFoundException


class ReturnTestObject(object):
    def __init__(self, attribute, value):
        setattr(self, attribute, value)


class Result(RowIterator):
    def __init__(self, return_object):
        self.num_results = 1 if return_object else 0
        self.return_object = return_object

    def __iter__(self):
        if isinstance(self.return_object, tuple):
            for _object in self.return_object:
                yield _object
        else:
            yield self.return_object


class QueryResultProvider(QueryJob):
    def __init__(self, return_object):
        self.return_object = return_object

    def result(self, timeout=None, retry=DEFAULT_RETRY):
        return Result(self.return_object)


class BigQueryTestClient(BigQueryClientWrapper):
    def __init__(self, query_return):
        self.query_result = QueryResultProvider(query_return)

    def query(
            self, *args, **kwargs):
        return self.query_result


class TestBigQuery(unittest.TestCase):
    def test_average_emails(self):
        self.assertEqual(3, InboxZeroBigQueryConnector(
            BigQueryTestClient(ReturnTestObject('average', 3))).average_inbox_count('A'))

    def test_average_emails_last_5_days(self):
        self.assertEqual(15, InboxZeroBigQueryConnector(
            BigQueryTestClient(ReturnTestObject('average', 15))).average_inbox_count('A', 5))

    def test_no_values_returned(self):
        self.assertRaises(NoValuesFoundException,
                          InboxZeroBigQueryConnector(
                              BigQueryTestClient(())).average_inbox_count, 'a')

    def test_quartiles(self):
        test_client = BigQueryTestClient((ReturnTestObject('quartile', 0),
                                          ReturnTestObject('quartile', 0),
                                          ReturnTestObject('quartile', 2),
                                          ReturnTestObject('quartile', 5),
                                          ReturnTestObject('quartile', 25)
                                          )
                                         )
        client = SuedSterneBigQueryClientWrapper()
        self.assertEqual(5, InboxZeroBigQueryConnector(test_client).quartile('Chris', 365, 3))
