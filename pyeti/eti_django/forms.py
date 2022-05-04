import datetime
import re

from django import forms
from django.forms.widgets import (
    Select, SplitDateTimeWidget as BaseSplitDateTimeWidget, Widget,
)
from django.utils.encoding import force_str
from django.utils.translation import gettext as _

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
            # Intentional bad super call.
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
            if isinstance(fieldset, str):
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


class AutofocusFirstFieldMixin(object):
    """
    A form mixin that adds an `autofocus` attribute to the first field that does
    not have an initial value.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            initial = self.initial.get(name, field.initial)
            if callable(initial):
                initial = initial()
            if not initial:
                self.fields[name].widget.attrs.update(autofocus=True)
                break


class SplitDateTimeWidget(BaseSplitDateTimeWidget):
    """
    A version of `SplitDateTimeWidget` from django core that allows you to
    explicitly pass the widgets that will be used for each component.

    For example, to make a neat little widget with both date and time split into
    select elements, do something like this:

        ```
        datetime = forms.SplitDateTimeField(
            input_date_formats=['%m-%d-%Y'],
            input_time_formats=['%I:%M%p'],
            required=True,
            widget=SplitDateTimeWidget(
                date_widget=SelectDateWidget(),
                time_widget=SelectTimeWidget(),
            )
        )
        ```
    """

    def __init__(self, date_widget=None, time_widget=None, attrs=None):
        if date_widget is None:
            date_widget = forms.DateInput(attrs=attrs)
        if time_widget is None:
            date_widget = forms.TimeInput(attrs=attrs)

        # Intentional bad super call.
        super(BaseSplitDateTimeWidget, self).__init__((date_widget, time_widget), attrs)


class SelectTimeWidget(Widget):
    """
    A Widget that splits time input into three <select> boxes for hour, minute,
    and meridiem (A.M. or P.M.). Mostly ripped from
    `django.forms.widgets.SelectDateWidget`. Currently has the following
    limitations due to laziness:

        - Can only do 12-hour time with meridiem (i.e. no military time).
        - Does not parse locale-based time formats. Instead, defaults to
          "{hour}:{minute}{meridiem}". This should not matter though, since the
          string value is never presented to the end user. This does require
          that the field that this widget represents declare a time format of
          "%I:%M%p" though.

    Accepts the following optional parameters:

        - hours: An iterable of hour values to display in the `hour` field, in
          case you want to limit the hours a user can select.
        - minutes: An iterable of minute values to display in the `minute` field,
          in case you want to limit the minutes a user can select.
        - attrs: Additional HTML attributes to include on the rendered widget.
        - empty_label: The empty label to use for each form element. Can be
          either a string or a 3-item iterable, where the values are the labels
          for the hour, minute, and meridiem fields, respectively.
    """
    hours = range(1, 13)
    minutes = range(0, 60)
    meridiems = (
        ('am', _('am')),
        ('pm', _('pm')),
    )

    none_value = ('', '---')
    hour_field = '%s_hour'
    minute_field = '%s_minute'
    meridiem_field = '%s_meridiem'

    template_name = 'eti_django/forms/widgets/select_time.html'

    input_type = 'select'
    select_widget = Select

    time_re = re.compile(r'(\d\d?):(\d{2})(am|pm)$')

    def __init__(self, hours=None, minutes=None, attrs=None, empty_label=None):
        self.attrs = attrs or {}

        if hours:
            self.hours = hours

        if minutes:
            self.minutes = minutes

        # Optional string, list, or tuple to use as empty_label.
        if isinstance(empty_label, (list, tuple)):
            if not len(empty_label) == 3:
                raise ValueError('empty_label list/tuple must have 3 elements.')

            self.hour_none_value = ('', empty_label[0])
            self.minute_none_value = ('', empty_label[1])
            self.meridiem_none_value = ('', empty_label[2])
        else:
            if empty_label is not None:
                self.none_value = ('', empty_label)

            self.hour_none_value = self.none_value
            self.minute_none_value = self.none_value
            self.meridiem_none_value = self.none_value

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        subwidgets = []

        hour_choices = [(i, force_str(i)) for i in self.hours]
        if self.is_required is False:
            hour_choices.insert(0, self.hour_none_value)
        hour_attrs = context['widget']['attrs'].copy()
        hour_name = self.hour_field % name
        hour_attrs['id'] = 'id_%s' % hour_name
        subwidgets.append(self.select_widget(attrs, choices=hour_choices).get_context(
            name=hour_name,
            value=context['widget']['value']['hour'],
            attrs=hour_attrs,
        )['widget'])

        minute_choices = [(i, '%02d' % i) for i in self.minutes]
        if self.is_required is False:
            minute_choices.insert(0, self.minute_none_value)
        minute_attrs = context['widget']['attrs'].copy()
        minute_name = self.minute_field % name
        minute_attrs['id'] = 'id_%s' % minute_name
        subwidgets.append(self.select_widget(attrs, choices=minute_choices).get_context(
            name=minute_name,
            value=context['widget']['value']['minute'],
            attrs=minute_attrs,
        )['widget'])

        meridiem_choices = [c for c in self.meridiems]
        if self.is_required is False:
            meridiem_choices.insert(0, self.meridiem_none_value)
        meridiem_attrs = context['widget']['attrs'].copy()
        meridiem_name = self.meridiem_field % name
        meridiem_attrs['id'] = 'id_%s' % meridiem_name
        subwidgets.append(self.select_widget(attrs, choices=meridiem_choices,).get_context(
            name=meridiem_name,
            value=context['widget']['value']['meridiem'],
            attrs=meridiem_attrs,
        )['widget'])

        context['widget']['subwidgets'] = subwidgets
        return context

    def format_value(self, value):
        hour, minute, meridiem = None, None, None
        if isinstance(value, (datetime.datetime, datetime.time)):
            hour, minute, meridiem = value.hour, value.minute, self.meridiems[int(value.hour < 12)][0]
        elif isinstance(value, str):
            match = self.time_re.match(value)
            if match:
                matches = match.groups()
                hour = int(matches[0])
                minute = int(matches[1])
                meridiem = matches[2]
        return {'hour': hour, 'minute': minute, 'meridiem': meridiem}

    def id_for_label(self, id_):
        return '%s_hour' % id_

    def value_from_datadict(self, data, files, name):
        hour = data.get(self.hour_field % name)
        minute = data.get(self.minute_field % name)
        meridiem = data.get(self.meridiem_field % name)
        if hour == minute == meridiem == '':
            return None
        if hour and minute and meridiem:
            return '%s:%02d%s' % (int(hour), int(minute), dict(self.meridiems)[meridiem])
        return data.get(name)

    def value_omitted_from_data(self, data, files, name):
        return not any(
            ('{}_{}'.format(name, interval) in data)
            for interval in ('hour', 'minute', 'meridiem')
        )
