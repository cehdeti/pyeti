try:
    from django.utils import six
except ImportError:
    import six

import dateutil.parser
from pyeti.utils import is_truthy


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


