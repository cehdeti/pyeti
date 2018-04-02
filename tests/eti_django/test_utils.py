from unittest import TestCase, mock
import six

from pyeti.eti_django.utils import typecast_from_field

from faker import Faker
faker = Faker()


class TypecastingFromFieldTests(TestCase):

    def test_returns_non_string_values_immediately(self):
        values = [3, 4.5, True, None, object()]

        for value in values:
            self.assertIs(typecast_from_field(mock.Mock(), value), value)

    def test_casts_blank_strings_to_null_for_fields_that_support_it(self):
        field = self.__mock_field(allow_null=True)
        self.assertIsNone(typecast_from_field(field, ''), None)
        self.assertIsNone(typecast_from_field(field, '   '), None)

    def test_casts_values_for_boolean_fields_to_a_boolean(self):
        field = self.__mock_field(field_type='BooleanField')
        values = {
            'y': True, 'Y': True, 'yes': True, 'YES': True, 'Yes': True,
            'no': False, '': False, 'NO': False, faker.word(): True, '': False,
        }

        for value, result in list(values.items()):
            self.assertIs(typecast_from_field(field, value), result, 'Failed for %s' % value)

    def test_strips_spaces_from_char_fields(self):
        field = self.__mock_field(field_type='CharField')
        values = {
            'hello': 'hello', '   hello': 'hello', 'hello   ': 'hello',
        }

        for value, result in list(values.items()):
            self.assertEqual(typecast_from_field(field, value), result)

    @mock.patch('pyeti.eti_django.utils.dateparse')
    def test_parses_values_for_date_fields_as_a_datetime_object(self, dateparse):
        return_value = faker.word()
        dateparse.parse_date.return_value = return_value
        field = self.__mock_field(field_type='DateField')
        value = faker.word()

        self.assertIs(typecast_from_field(field, value), return_value)
        dateparse.parse_date.assert_called_once_with(value)

    def test_casts_values_for_simpler_fields_using_builtin_casting_functions(self):
        conversions = [
            ('FloatField', '__float__', 'pyfloat'),
            ('IntegerField', '__int__', 'pyint'),
        ]

        for field_type, conversion_method, mock_method in conversions:
            field = self.__mock_field(field_type=field_type)
            return_value = getattr(faker, mock_method)()
            value = mock.MagicMock()
            value.__class__ = six.string_types[0]
            converter = mock.MagicMock(return_value=return_value)
            setattr(value, conversion_method, converter)

            self.assertIs(typecast_from_field(field, value), return_value)
            self.assertTrue(getattr(value, conversion_method).called)

    def test_returns_values_we_dont_know_how_to_deal_with(self):
        field = self.__mock_field(field_type='SomeRandomField')
        value = faker.word()
        self.assertIs(typecast_from_field(field, value), value)

    def __mock_field(self, field_type='CharField', allow_null=False):
        field = mock.Mock()
        field_option = mock.Mock()
        field_option.get.return_value = allow_null
        field.deconstruct.return_value = [field_option]
        field.get_internal_type.return_value = field_type
        return field
