import collections
from datetime import date, timedelta
from unittest import TestCase

from pyeti.datetime_utils import enumerate_days


class EnumerateDaysTests(TestCase):

    def test_correct_number_of_days(self):
        start_date = date(2019, 1, 1)
        end_date = date(2019, 1, 30)

        day_list = list(enumerate_days(start_date, end_date))
        self.assertEqual(30, len(day_list))

    def test_is_iterator(self):
        start_date = date(2019, 1, 1)
        end_date = date(2019, 1, 30)
        day_iterator = enumerate_days(start_date, end_date)
        self.assertIsInstance(day_iterator, collections.Iterator)

    def test_no_end_date(self):
        start_date = date.today() - timedelta(days=29)
        day_list = list(enumerate_days(start_date))
        self.assertEqual(30, len(day_list))
