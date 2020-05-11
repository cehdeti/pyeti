import datetime
import re
import six


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
_no_values = ['n', 'no', '0', 'false', '']


def is_truthy(value):
    """
    Utility function that converts various values to a boolean. Useful for web
    requests, where the value that comes in may be "0" or "false", etc.
    """
    if isinstance(value, six.string_types):
        value = value.strip().lower()

        if value in _yes_values:
            return True
        if value in _no_values:
            return False

    return bool(value)


_integer_re = re.compile(r'^\-?[\d,]*$')
_float_re = re.compile(r'^[-+]?[\d,]*\.?\d+([eE][-+]?\d+)?$')


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


_non_numeric_re = re.compile(r'[^-\d\.]')


def clean_numeric_string(value):
    """
    Removes extraneous characters (commas, spaces, etc.) from number-like
    strings.
    """
    return _non_numeric_re.sub('', value)


class AgeMixin(object):
    """
    Calculates the age of a person given a DateField of a person's birthday
    """

    BIRTH_DATE_FIELD = 'birth_date'

    @property
    def age(self):
        """
        The age today.
        """
        return self.age_on(datetime.date.today())

    def age_on(self, date):
        """
        Returns the age on the given date.
        """
        birth_date = getattr(self, self.BIRTH_DATE_FIELD)

        if not birth_date:
            return

        if birth_date > date:
            raise ValueError('Birth date after %s!' % date)

        return date.year - birth_date.year - (
            (date.month, date.day) < (birth_date.month, birth_date.day)
        )


class classproperty(property):
    """
    Allows for setting dynamic properties on a class and its instances.

    Example:
        ```
        class MyThing:

            @classproperty
            def foo(cls):
                return 'hello'

        MyThing.foo => 'hello'
        MyThing().foo => 'hello'
    """

    def __get__(self, obj, objtype=None):
        return super().__get__(objtype)

    def __set__(self, obj, value):
        super().__set__(type(obj), value)

    def __delete__(self, obj):
        super().__delete__(type(obj))
