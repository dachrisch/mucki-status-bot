# coding=UTF-8
import unittest
from json import dumps

from google_service_api.welfare import WelfareStatus


class DummySheetConnector:
    def __init__(self, dummy_range):
        self.__range = dummy_range

    def values_for_range(self, sheet_range):
        return dumps(self.__range)


class TestShout(unittest.TestCase):
    def test_all_OK(self):
        welfare_status = WelfareStatus(DummySheetConnector((('A', 'OK', None, None, None, None),
                                                            ('B', 'OK', None, None, None, None),
                                                            ('C', 'OK', None, None, None, None),
                                                            ('D', 'OK', None, None, None, None),
                                                            ('E', 'OK', None, None, None, None),
                                                            ('F', 'OK', None, None, None, None),
                                                            ('G', 'OK', None, None, None, None),
                                                            ('H', 'OK', None, None, None, None))))
        self.assertEqual('unicorn dance', welfare_status.shoutout)

    def test_7_8_OK(self):
        welfare_status = WelfareStatus(DummySheetConnector((('A', 'Überlast', None, None, None, None),
                                                            ('B', 'OK', None, None, None, None),
                                                            ('C', 'OK', None, None, None, None),
                                                            ('D', 'OK', None, None, None, None),
                                                            ('E', 'OK', None, None, None, None),
                                                            ('F', 'OK', None, None, None, None),
                                                            ('G', 'OK', None, None, None, None),
                                                            ('H', 'OK', None, None, None, None))))
        self.assertEqual('well', welfare_status.shoutout)

    def test_6_8_OK(self):
        welfare_status = WelfareStatus(DummySheetConnector((('A', 'Überlast', None, None, None, None),
                                                            ('B', 'Überlast', None, None, None, None),
                                                            ('C', 'OK', None, None, None, None),
                                                            ('D', 'OK', None, None, None, None),
                                                            ('E', 'OK', None, None, None, None),
                                                            ('F', 'OK', None, None, None, None),
                                                            ('G', 'OK', None, None, None, None),
                                                            ('H', 'OK', None, None, None, None))))
        self.assertEqual('well', welfare_status.shoutout)

    def test_5_8_OK(self):
        welfare_status = WelfareStatus(DummySheetConnector((('A', 'Überlast', None, None, None, None),
                                                            ('B', 'Überlast', None, None, None, None),
                                                            ('C', 'Überlast', None, None, None, None),
                                                            ('D', 'OK', None, None, None, None),
                                                            ('E', 'OK', None, None, None, None),
                                                            ('F', 'OK', None, None, None, None),
                                                            ('G', 'OK', None, None, None, None),
                                                            ('H', 'OK', None, None, None, None))))
        self.assertEqual('well', welfare_status.shoutout)

    def test_4_8_OK(self):
        welfare_status = WelfareStatus(DummySheetConnector((('A', 'Überlast', None, None, None, None),
                                                            ('B', 'Überlast', None, None, None, None),
                                                            ('C', 'Überlast', None, None, None, None),
                                                            ('D', 'Überlast', None, None, None, None),
                                                            ('E', 'OK', None, None, None, None),
                                                            ('F', 'OK', None, None, None, None),
                                                            ('G', 'OK', None, None, None, None),
                                                            ('H', 'OK', None, None, None, None))))
        self.assertEqual('crying', welfare_status.shoutout)

    def test_3_8_OK(self):
        welfare_status = WelfareStatus(DummySheetConnector((('A', 'Überlast', None, None, None, None),
                                                            ('B', 'Überlast', None, None, None, None),
                                                            ('C', 'Überlast', None, None, None, None),
                                                            ('D', 'Überlast', None, None, None, None),
                                                            ('E', 'Überlast', None, None, None, None),
                                                            ('F', 'OK', None, None, None, None),
                                                            ('G', 'OK', None, None, None, None),
                                                            ('H', 'OK', None, None, None, None))))
        self.assertEqual('crying', welfare_status.shoutout)

    def test_2_8_OK(self):
        welfare_status = WelfareStatus(DummySheetConnector((('A', 'Überlast', None, None, None, None),
                                                            ('B', 'Überlast', None, None, None, None),
                                                            ('C', 'Überlast', None, None, None, None),
                                                            ('D', 'Überlast', None, None, None, None),
                                                            ('E', 'Überlast', None, None, None, None),
                                                            ('F', 'Überlast', None, None, None, None),
                                                            ('G', 'OK', None, None, None, None),
                                                            ('H', 'OK', None, None, None, None))))
        self.assertEqual('crying', welfare_status.shoutout)

    def test_1_8_OK(self):
        welfare_status = WelfareStatus(DummySheetConnector((('A', 'Überlast', None, None, None, None),
                                                            ('B', 'Überlast', None, None, None, None),
                                                            ('C', 'Überlast', None, None, None, None),
                                                            ('D', 'Überlast', None, None, None, None),
                                                            ('E', 'Überlast', None, None, None, None),
                                                            ('F', 'Überlast', None, None, None, None),
                                                            ('G', 'Überlast', None, None, None, None),
                                                            ('H', 'OK', None, None, None, None))))
        self.assertEqual('crying', welfare_status.shoutout)

    def test_0_8_OK(self):
        welfare_status = WelfareStatus(DummySheetConnector((('A', 'Überlast', None, None, None, None),
                                                            ('B', 'Überlast', None, None, None, None),
                                                            ('C', 'Überlast', None, None, None, None),
                                                            ('D', 'Überlast', None, None, None, None),
                                                            ('E', 'Überlast', None, None, None, None),
                                                            ('F', 'Überlast', None, None, None, None),
                                                            ('G', 'Überlast', None, None, None, None),
                                                            ('H', 'Überlast', None, None, None, None))))
        self.assertEqual('panic scared', welfare_status.shoutout)


if __name__ == '__main__':
    unittest.main()
