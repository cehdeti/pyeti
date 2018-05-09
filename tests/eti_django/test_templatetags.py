from unittest import TestCase

from django.test import RequestFactory
from faker import Faker

from pyeti.eti_django.templatetags.html import unique_html_id

fake = Faker()


class UniqueHtmlIdTests(TestCase):

    def setUp(self):
        super().setUp()
        self.__context = {'request': RequestFactory()}

    def test_returns_a_unique_id(self):
        word = fake.word()
        self.assertEqual(word, unique_html_id(self.__context, word))
        second = unique_html_id(self.__context, word)
        self.assertNotEqual(word, second)
        self.assertIn(word, second)

    def test_raises_if_there_is_no_request_in_the_context(self):
        self.assertRaises(Exception, unique_html_id, {}, fake.word())
