from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import dateparse

from pyeti.utils import is_truthy

_TYPECASTERS = {
    models.BooleanField: lambda x: is_truthy(x),
    models.CharField: lambda x: x.strip(),
    models.DateField: lambda x: dateparse.parse_date(x),
    models.FloatField: lambda x: float(x),
    models.IntegerField: lambda x: int(x),
    ArrayField: lambda x: x.split(',') if x.strip() else [],
}


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

    for field_class, typecaster in _TYPECASTERS.items():
        if isinstance(field, field_class):
            return typecaster(value)

    return value
