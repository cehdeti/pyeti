from unittest import TestCase

from django import forms

from pyeti.eti_django.forms import ConfirmationFieldMixin


class ConfirmationFieldMixinTests(TestCase):

    class TestForm(ConfirmationFieldMixin, forms.Form):

        field_1 = forms.CharField()
        field_1_confirm = forms.CharField()
        field_2 = forms.CharField(label='My Field')
        confirm_field_2 = forms.CharField(label='Confirm my field')
        field_3 = forms.CharField()
        field_3_confirm = forms.CharField()

        CONFIRMATION_FIELDS = (
            'field_1',
            ('field_2', 'confirm_field_2'),
            'field_3'
        )

    def test_it_raises_an_error_for_all_confirmation_fields_that_do_not_match(self):
        form = self.TestForm({
            'field_1': 'hello', 'field_1_confirm': 'hello2',
            'field_2': 'hello', 'confirm_field_2': 'hello2',
            'field_3': 'hello', 'field_3_confirm': 'hello',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('field_1_confirm', form.errors)
        self.assertIn('confirm_field_2', form.errors)
        self.assertNotIn('field_3_confirm', form.errors)

    def test_does_not_raise_when_the_fields_match(self):
        form = self.TestForm({
            'field_1': 'hello', 'field_1_confirm': 'hello',
            'field_2': 'hello2', 'confirm_field_2': 'hello2',
            'field_3': 'hello3', 'field_3_confirm': 'hello3',
        })
        self.assertTrue(form.is_valid())

    def test_raises_when_confirmation_fields_is_something_else(self):
        form = self.TestForm({
            'field_1': 'hello', 'field_1_confirm': 'hello',
        })
        form.CONFIRMATION_FIELDS = (
            ('field_1', 'field_1_confirm', 'another_thing'),
        )
        self.assertRaises(Exception, form.is_valid)
