try:
    from django.utils import six
except ImportError:
    import six

import re
import dateutil.parser


class empty_context(object):
    """
    A silly little context manager that essentially does nothing. Useful with
    conditional `with` statements:

        ```
        with transaction.atomic() if transact else empty_context():
            ...
        ```
    """

    def __enter__(self):
        return None

    def __exit__(self, *_):
        return False

    def __call__(self):
        return self

empty_context = empty_context()


def ignore_exception(*exception_classes):
    """
    A function decorator to catch exceptions and pass.

        @ignore_exception(ValueError, ZeroDivisionError)
        def my_function():
            ...

    Note that this functionality should only be used when you don't care about
    the return value of the function, as it will return `None` if an exception
    is caught.
    """
    def decorator(func):
        def func_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (exception_classes):
                pass
        return func_wrapper
    return decorator


_yes_values = ['y', 'yes', '1', 'true']


def is_truthy(value):
    """
    Utility function that converts various values to a boolean. Useful for web
    requests, where the value that comes in may be "0" or "false", etc.
    """
    if isinstance(value, six.string_types):
        value = value.lower()
        return value.lower() in _yes_values

    return bool(value)


def typecast_from_field(field, value):
    """
    Given a Django model field and a value, typecast the value to the datatype
    expected by the field.
    """
    if not isinstance(value, six.string_types):
        return value
    if field.deconstruct()[-1].get('null') and value.strip() == '':
        return None

    field_type = field.get_internal_type()
    if field_type == 'BooleanField':
        return is_truthy(value)
    if field_type == 'CharField':
        return value.strip()
    if field_type == 'DateField':
        return dateutil.parser.parse(value)
    if field_type == 'FloatField':
        return float(value)
    if field_type == 'IntegerField':
        return int(value)

    return value


_integer_re = re.compile('^\-?[\d,]*$')
_float_re = re.compile('^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$')


def typecast_guess(value):
    """
    Try to typecast the given string value into a proper python datatype.
    """
    if not isinstance(value, six.string_types):
        return value

    stripped = value.strip()
    if stripped == '':
        return None
    if _integer_re.match(value):
        return int(clean_numeric_string(value))
    if _float_re.match(value):
        return float(clean_numeric_string(value))
    return stripped


def clean_numeric_string(value):
    """
    Removes extraneous characters (commas, spaces, etc.) from number-like
    strings.
    """
    return value \
        .replace(',', '') \
        .replace(' ', '') \
        .strip()
