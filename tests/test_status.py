# coding=UTF-8
import unittest

from telegram_service.status import calculate_team_rating, team_rating_to_shoutout


class TestStatus(unittest.TestCase):
    def test_one_OK(self):
        status = {'A': 'OK'}
        self.assertEqual(1, calculate_team_rating(status))

    def test_half_OK(self):
        status = {'A': 'OK', 'B': 'Überlast'}
        self.assertEqual(.5, calculate_team_rating(status))

    def test_none_OK(self):
        status = {'A': 'Überlast', 'B': 'Überlast'}
        self.assertEqual(0, calculate_team_rating(status))

    def test_almost_all_OK(self):
        status = {'A': 'OK', 'B': 'OK', 'C': 'OK', 'D': 'OK', 'E': 'OK', 'F': 'Überlast'}
        self.assertEqual(5.0 / 6, calculate_team_rating(status))


class TestShout(unittest.TestCase):
    def test_all_OK(self):
        status = {'A': 'OK', 'B': 'OK', 'C': 'OK', 'D': 'OK', 'E': 'OK', 'F': 'OK', 'G': 'OK', 'H': 'OK'}
        self.assertEqual('unicorn dance', team_rating_to_shoutout(status))

    def test_7_8_OK(self):
        status = {'A': 'OK', 'B': 'OK', 'C': 'OK', 'D': 'OK', 'E': 'OK', 'F': 'OK', 'G': 'OK', 'H': 'Überlast'}
        self.assertEqual('well', team_rating_to_shoutout(status))

    def test_6_8_OK(self):
        status = {'A': 'OK', 'B': 'OK', 'C': 'OK', 'D': 'OK', 'E': 'OK', 'F': 'OK', 'G': 'Überlast', 'H': 'Überlast'}
        self.assertEqual('well', team_rating_to_shoutout(status))

    def test_5_8_OK(self):
        status = {'A': 'OK', 'B': 'OK', 'C': 'OK', 'D': 'OK', 'E': 'OK', 'F': 'Überlast', 'G': 'Überlast',
                  'H': 'Überlast'}
        self.assertEqual('well', team_rating_to_shoutout(status))

    def test_4_8_OK(self):
        status = {'A': 'OK', 'B': 'OK', 'C': 'OK', 'D': 'OK', 'E': 'Überlast', 'F': 'Überlast', 'G': 'Überlast',
                  'H': 'Überlast'}
        self.assertEqual('crying', team_rating_to_shoutout(status))

    def test_3_8_OK(self):
        status = {'A': 'OK', 'B': 'OK', 'C': 'OK', 'D': 'Überlast', 'E': 'Überlast', 'F': 'Überlast', 'G': 'Überlast',
                  'H': 'Überlast'}
        self.assertEqual('crying', team_rating_to_shoutout(status))

    def test_2_8_OK(self):
        status = {'A': 'OK', 'B': 'OK', 'C': 'Überlast', 'D': 'Überlast', 'E': 'Überlast', 'F': 'Überlast',
                  'G': 'Überlast', 'H': 'Überlast'}
        self.assertEqual('crying', team_rating_to_shoutout(status))

    def test_1_8_OK(self):
        status = {'A': 'OK', 'B': 'Überlast', 'C': 'Überlast', 'D': 'Überlast', 'E': 'Überlast', 'F': 'Überlast',
                  'G': 'Überlast', 'H': 'Überlast'}
        self.assertEqual('crying', team_rating_to_shoutout(status))

    def test_0_8_OK(self):
        status = {'A': 'Überlast', 'B': 'Überlast', 'C': 'Überlast', 'D': 'Überlast', 'E': 'Überlast', 'F': 'Überlast',
                  'G': 'Überlast', 'H': 'Überlast'}
        self.assertEqual('panic scared', team_rating_to_shoutout(status))


if __name__ == '__main__':
    unittest.main()
