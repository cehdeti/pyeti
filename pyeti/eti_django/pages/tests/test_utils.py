from unittest import TestCase

from pyeti.eti_django.pages.utils import parse_placeholders


class ParsePlaceholdersTests(TestCase):

    def test_parses_a_single_placeholder(self):
        subjects = [
            '{% placeholder "Test Placeholder" %}',
            'Stuff before {% placeholder "Test Placeholder" %}',
            '{% placeholder "Test Placeholder" %} stuff after',
            'Hello hello, this is a {% placeholder "Test Placeholder" %} placeholder!!!',
            "Hello hello, this is a {% placeholder 'Test Placeholder' %} placeholder!!!",
            'Hello hello, this is a {% placeholder "Test Placeholder" "en" %} placeholder!!!',
        ]

        for subject in subjects:
            self.assertEqual(['Test Placeholder'], parse_placeholders(subject))

    def test_parses_multiple_placeholders(self):
        subjects = [
            '{% placeholder "First" %}{% placeholder "Second" %}',
            '{% placeholder "First" %} {% placeholder "Second" %}',
            '{% placeholder "First" %} {% placeholder \'Second\' %}',
            '{% placeholder "First" "en" %} {% placeholder "Second" "fr" %}',
            'Stuff before {% placeholder "First" %} {% placeholder "Second" %}',
            '{% placeholder "First" %} {% placeholder "Second" %} stuff after',
            '{% placeholder "First" %} stuff between {% placeholder "Second" %}',
            'Hello hello, {% placeholder "First" %} placeholder {% placeholder "Second" %} placeholder!!!',
        ]

        for subject in subjects:
            self.assertEqual(['First', 'Second'], parse_placeholders(subject))
