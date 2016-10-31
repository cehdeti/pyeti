from unittest import TestCase

from pyeti.utils import ignore_exception


class IgnoreExceptionTests(TestCase):
    def test_swallows_the_exception(self):
        @ignore_exception(ValueError)
        def some_func():
            raise ValueError()
        some_func()

    def test_does_not_swallow_other_exceptions(self):
        @ignore_exception(ValueError)
        def some_func():
            raise KeyError()

        self.assertRaises(KeyError, some_func)

    def test_allows_a_list_of_exception_classes(self):
        @ignore_exception(ValueError, KeyError)
        def some_func():
            raise KeyError()
        some_func()
