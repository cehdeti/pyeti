from unittest import TestCase

from pyeti.utils import empty_context


class InstanceTests(TestCase):
    def test_works(self):
        with empty_context():
            hello = 'hello'
        self.assertEqual(hello, 'hello')


class ClassTests(TestCase):
    def test_works(self):
        with empty_context:
            hello = 'hello'
        self.assertEqual(hello, 'hello')
