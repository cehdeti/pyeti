from unittest import TestCase, mock

from datetime import date

from pyeti.utils import AgeMixin

from faker import Faker
fake = Faker()


class AgeMixinTests(TestCase):

    def setUp(self):
        super().setUp()
        date_patcher = mock.patch('pyeti.utils.date')
        mock_date = date_patcher.start()
        mock_date.today.return_value = date(2018, 4, 1)
        self.addCleanup(date_patcher.stop)

    def test_returns_the_correct_age(self):
        tests = {
            date(1953, 3, 31): 65,
            date(1953, 5, 21): 64,
            date(2018, 4, 1): 0,
            date(2018, 3, 31): 0,
        }

        obj = _AgeMixinImplementation()

        for birth_date, expected_age in tests.items():
            obj.birth_date = birth_date
            self.assertEqual(obj.age, expected_age)

    def test_uses_the_specified_birth_date_field(self):
        attr = fake.word()
        obj = _AgeMixinImplementation(attr=attr)
        setattr(obj, attr, date(1953, 3, 21))
        self.assertEqual(65, obj.age)

    def test_returns_null_if_there_is_no_birth_date(self):
        obj = _AgeMixinImplementation()
        self.assertIsNone(obj.age)

    def test_raises_if_birth_date_is_somehow_in_the_future(self):
        obj = _AgeMixinImplementation(date(2018, 9, 4))
        with self.assertRaises(ValueError):
            obj.age


class _AgeMixinImplementation(AgeMixin):

    def __init__(self, birth_date=None, attr=AgeMixin.BIRTH_DATE_FIELD):
        self.birth_date = birth_date
        self.BIRTH_DATE_FIELD = attr
