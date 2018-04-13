from django import forms
from django.utils import six
from django.utils.translation import ugettext as _

try:
    from django.contrib.postgres.fields import ArrayField
except ImportError:
    ArrayField = None


if ArrayField:
    class ChoiceArrayField(ArrayField):
        """
        A field that allows us to store an array of choices.

        Uses Django 1.9+ postgres ArrayField and a MultipleChoiceField for its
        formfield.

        https://blogs.gnome.org/danni/2016/03/08/multiple-choice-using-djangos-postgres-arrayfield/
        """

        def formfield(self, **kwargs):
            defaults = {
                'form_class': forms.MultipleChoiceField,
                'choices': self.base_field.choices,
            }
            defaults.update(kwargs)
            # Skip our parent's formfield implementation completely as we don't
            # care for it.
            # pylint:disable=bad-super-call
            return super(ArrayField, self).formfield(**defaults)


class ConfirmationFieldMixin(object):
    """
    Form mixin for ensuring that confirmation fields match. A common use case is
    for password or email confirmation fields, where the values of the 2 fields
    must be the same.

    Use as follows:

        class MyForm(ConfirmationFieldMixin, forms.Form):

            email = forms.CharField()
            email_confirm = forms.CharField()

            CONFIRMATION_FIELDS = [
                ('email', 'email_confirm')
            ]

    The `CONFIRMATION_FIELDS` property must be a list where each item is one of
    the following:

        - A string containing the name of the field to check. The name of the
            confirmation field is assumed to be "{field}_confirm".
        - A 2-tuple where the first item is the name of the field and the second
            is the name of the confirmation field.
    """

    CONFIRMATION_FIELDS = []

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        errors = {}

        for fieldset in self.CONFIRMATION_FIELDS:
            if isinstance(fieldset, six.string_types):
                field_1 = fieldset
                field_2 = '%s_confirm' % fieldset
            elif len(fieldset) == 2:
                field_1, field_2 = fieldset
            else:
                raise Exception('Confirmation fields must be either a string or a 2-tuple')

            if cleaned_data[field_1] == cleaned_data[field_2]:
                continue

            errors[field_2] = _('%(field_1)s and %(field_2)s fields do not match') % {
                'field_1': self.fields[field_1].get_bound_field(self, field_1).label,
                'field_2': self.fields[field_2].get_bound_field(self, field_2).label,
            }

        if len(errors) > 0:
            raise forms.ValidationError(errors)

        return cleaned_data
