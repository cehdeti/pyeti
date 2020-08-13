from unittest import TestCase

from django.test import RequestFactory
from django.utils.html import conditional_escape
from faker import Faker

from pyeti.eti_django.templatetags.email import obfuscate, obfuscate_mailto
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


class ObfuscateEmailTests(TestCase):

    def test_obfuscates_email(self):
        self.assertEqual(
            obfuscate('test@example.com'),
            '&#116;&#101;&#115;&#116;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;'
        )

    def test_obfuscating_email_marks_string_as_safe(self):
        result = obfuscate('<script>')
        self.assertEqual(result, conditional_escape(result))

    def test_obfuscates_mailto_links(self):
        self.assertEqual(
            obfuscate_mailto('test@example.com'),
            '<a href="&#109;&#97;ilto:&#116;&#101;&#115;&#116;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;">&#116;&#101;&#115;&#116;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;</a>'
        )

    def test_obfuscates_mailto_handles_link_text(self):
        self.assertEqual(
            obfuscate_mailto('test@example.com', text='Hello'),
            '<a href="&#109;&#97;ilto:&#116;&#101;&#115;&#116;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;">Hello</a>'
        )

    def test_obfuscates_mailto_handles_link_subject(self):
        self.assertEqual(
            obfuscate_mailto('test@example.com', text=';This is the subject'),
            '<a href="&#109;&#97;ilto:&#116;&#101;&#115;&#116;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;?subject=This%20is%20the%20subject">&#116;&#101;&#115;&#116;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;</a>'
        )

    def test_obfuscates_mailto_handles_link_text_and_subject(self):
        self.assertEqual(
            obfuscate_mailto('test@example.com', text='Hello;This is the subject'),
            '<a href="&#109;&#97;ilto:&#116;&#101;&#115;&#116;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;?subject=This%20is%20the%20subject">Hello</a>'
        )

    def test_obfuscates_mailto_handles_xss_in_link_text(self):
        self.assertEqual(
            obfuscate_mailto('test@example.com', text='<script></script>'),
            '<a href="&#109;&#97;ilto:&#116;&#101;&#115;&#116;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;">&lt;script&gt;&lt;/script&gt;</a>'
        )

    def test_obfuscates_mailto_handles_xss_in_link_subject(self):
        self.assertEqual(
            obfuscate_mailto('test@example.com', text=';<script></script>'),
            '<a href="&#109;&#97;ilto:&#116;&#101;&#115;&#116;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;?subject=%26lt%3Bscript%26gt%3B%26lt%3B/script%26gt%3B">&#116;&#101;&#115;&#116;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;</a>'
        )

    def test_obfuscates_mailto_handles_attributes(self):
        self.assertEqual(
            obfuscate_mailto('test@example.com', text='Hello', attr='testing', disabled=True),
            '<a attr="testing" href="&#109;&#97;ilto:&#116;&#101;&#115;&#116;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;" disabled>Hello</a>'
        )
