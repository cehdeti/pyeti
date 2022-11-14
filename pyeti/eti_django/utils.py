from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import dateparse

from pyeti.utils import is_truthy


def typecast_from_field(field, value):
    """
    Given a Django model field and a value, typecast the value to the datatype
    expected by the field.
    """
    if not isinstance(value, str):
        return value

    options = field.deconstruct()[-1]

    if options.get('null') and value.strip() == '':
        return None

    if 'choices' in options:
        for choice, label in options['choices']:
            if value == label:
                return choice

    if isinstance(field, ArrayField):
        return _parse_arrayfield(value, options['base_field'])

    for field_class, typecaster in _TYPECASTERS.items():
        if isinstance(field, field_class):
            return typecaster(value)

    return value


def _parse_arrayfield(value, base_field):
    if value.strip() == '':
        return []

    return [
        typecast_from_field(base_field, val)
        for val in value.split(',')
    ]


_TYPECASTERS = {
    models.BooleanField: is_truthy,
    models.CharField: lambda value: value.strip(),
    models.DateField: dateparse.parse_date,
    models.FloatField: float,
    models.IntegerField: int,
}
