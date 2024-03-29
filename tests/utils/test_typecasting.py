from unittest import TestCase

from faker import Faker

from pyeti.utils import typecast_guess

faker = Faker()


class TypecastingGuessTests(TestCase):

    def test_returns_immediately_for_non_strings(self):
        value = faker.pyint()
        self.assertIs(typecast_guess(value), value)

    def test_casts_blank_strings_to_null(self):
        for value in [
            '', '   ',
            'NA', 'nA', 'n/a', 'N/a',
            'None', 'nOne'
        ]:
            with self.subTest(value=value):
                self.assertIsNone(typecast_guess(value), None)

    def test_casts_various_values_correctly(self):
        conversions = {
            '4': 4, '-4': -4, '0': 0, '4.2': 4.2, '-4.2': -4.2, '.334': 0.334,
            '0.44': 0.44, 'hello': 'hello', '34,203.2': 34203.2,
            '3.9233193446698323e+02': 392.3319344669832,
            '1.7000000178813934e-01': 0.17000000178813934,
        }

        for value, result in list(conversions.items()):
            with self.subTest(value=value, result=result):
                self.assertEqual(typecast_guess(value), result)
