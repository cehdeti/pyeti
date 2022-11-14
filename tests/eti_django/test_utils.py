from datetime import date
from unittest import TestCase, mock

from django.contrib.postgres.fields import ArrayField
from django.db import models
from faker import Faker

from pyeti.eti_django.utils import typecast_from_field

faker = Faker()


class _FakeField(models.Field):
    pass


class TypecastingFromFieldTests(TestCase):

    def test_returns_non_string_values_immediately(self):
        values = [3, 4.5, True, None, object()]

        for value in values:
            self.assertIs(typecast_from_field(mock.Mock(), value), value)

    def test_casts_blank_strings_to_null_for_fields_that_support_it(self):
        field = self.__mock_field(null=True)
        self.assertIsNone(typecast_from_field(field, ''), None)
        self.assertIsNone(typecast_from_field(field, '   '), None)

    def test_casts_values_for_boolean_fields_to_a_boolean(self):
        field = self.__mock_field(field_class=models.BooleanField)
        values = {
            'y': True, 'Y': True, 'yes': True, 'YES': True, 'Yes': True,
            'no': False, '': False, 'NO': False, faker.word(): True, '': False,
        }

        for value, result in list(values.items()):
            self.assertIs(typecast_from_field(field, value), result, 'Failed for %s' % value)

    def test_strips_spaces_from_char_fields(self):
        field = self.__mock_field()
        values = {
            'hello': 'hello', '   hello': 'hello', 'hello   ': 'hello',
        }

        for value, result in list(values.items()):
            self.assertEqual(typecast_from_field(field, value), result)

    def test_parses_values_for_date_fields_as_a_date_object(self):
        field = self.__mock_field(field_class=models.DateField)
        self.assertEqual(
            typecast_from_field(field, '2011-11-12'),
            date(2011, 11, 12)
        )

    def test_casts_values_for_simpler_fields_using_builtin_casting_functions(self):
        conversions = [
            (models.FloatField, '__float__', 'pyfloat'),
            (models.IntegerField, '__int__', 'pyint'),
        ]

        for field_class, conversion_method, mock_method in conversions:
            field = self.__mock_field(field_class=field_class)
            return_value = getattr(faker, mock_method)()
            value = mock.MagicMock()
            value.__class__ = str
            converter = mock.MagicMock(return_value=return_value)
            setattr(value, conversion_method, converter)

            self.assertIs(typecast_from_field(field, value), return_value)
            self.assertTrue(getattr(value, conversion_method).called)

    def test_casts_values_for_array_fields_to_a_list(self):
        base_field = self.__mock_field(field_class=models.CharField)
        field = self.__mock_field(field_class=ArrayField, base_field=base_field)
        value = typecast_from_field(field, 'hello,there')
        self.assertIsInstance(value, list)
        self.assertEqual(value, ['hello', 'there'])

    def test_handles_empty_array_fields(self):
        base_field = self.__mock_field(field_class=models.CharField)
        field = self.__mock_field(field_class=ArrayField, base_field=base_field)
        value = typecast_from_field(field, '')
        self.assertIsInstance(value, list)
        self.assertEqual(value, [])

    def test_maps_choice_labels_to_values_for_fields_with_choices(self):
        field = self.__mock_field(field_class=models.IntegerField, choices=[(1, 'Hello'), (2, 'There')])
        value = typecast_from_field(field, 'Hello')
        self.assertIsInstance(value, int)
        self.assertEqual(value, 1)

    def test_handles_array_fields_with_choices(self):
        base_field = self.__mock_field(field_class=models.CharField, choices=[(1, 'Hello'), (2, 'There')])
        field = self.__mock_field(field_class=ArrayField, base_field=base_field)
        value = typecast_from_field(field, 'Hello,There')
        self.assertIsInstance(value, list)
        self.assertEqual(value, [1, 2])

    def test_returns_values_we_dont_know_how_to_deal_with(self):
        field = self.__mock_field(field_class=_FakeField)
        value = faker.word()
        self.assertIs(typecast_from_field(field, value), value)

    def __mock_field(self, field_class=models.CharField, **options):
        options.setdefault('null', False)

        field = mock.Mock(spec=field_class)
        field_options = options
        field.deconstruct.return_value = [field_options]
        return field
