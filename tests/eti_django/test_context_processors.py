from unittest import TestCase

from pyeti.eti_django.context_processors import marquee


class _Request(object):
    def __init__(self, dict_={}):
        for k, v in dict_.items():
            setattr(self, k, v)


class MarqueeTests(TestCase):

    def test_handles_string_values(self):
        cases = {'1': True, '0': False, 'True': True, 'False': False}

        for value, result in cases.items():
            request = _Request({'GET': {'marquee': value}})
            self.assertIs(marquee(request)['marquee'], result)

    def test_defaults_to_false(self):
        request = _Request({'GET': {}})
        self.assertFalse(marquee(request)['marquee'])
