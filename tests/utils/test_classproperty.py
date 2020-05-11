from unittest import TestCase

from pyeti.utils import classproperty


class _MyClass:

    @classproperty
    def foo(cls):
        return cls.__name__.replace('_', '').lower()


class _MySubclass(_MyClass):
    pass


class ClassPropertyTests(TestCase):

    def test_sets_the_property_on_the_class(self):
        self.assertEqual(_MyClass.foo, 'myclass')

    def test_sets_the_property_on_instances_of_the_class(self):
        self.assertEqual(_MyClass().foo, 'myclass')

    def test_works_with_subclasses(self):
        self.assertEqual(_MySubclass.foo, 'mysubclass')
