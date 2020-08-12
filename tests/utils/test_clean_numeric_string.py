from unittest import TestCase

from faker import Faker

from pyeti.utils import clean_numeric_string

faker = Faker()


class CleanNumericStringTests(TestCase):

    def test_removes_all_nonnumeric_characters(self):
        tests = {
            '123,125.211': '123125.211',
            '   1245 ': '1245',
            'abc12$125,124.4': '12125124.4',
            '1234': '1234',
            '$-134.31': '-134.31',
        }

        for value, expected in tests.items():
            self.assertEqual(clean_numeric_string(value), expected)

    def test_only_works_on_strings(self):
        self.assertRaises(TypeError, clean_numeric_string, 1234)

    def test_works_on_blank_strings(self):
        self.assertEqual('', clean_numeric_string(''))
