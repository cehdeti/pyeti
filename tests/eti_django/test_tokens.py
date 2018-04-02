from unittest import TestCase, mock
from faker import Faker

from django.db import models
from django.db.utils import OperationalError

from pyeti.eti_django.tokens import TokenGenerator, HasSecureTokenMixin


faker = Faker()


class TokenGeneratorTests(TestCase):

    def setUp(self):
        super().setUp()
        self.__mock_settings = mock.patch('pyeti.eti_django.tokens.settings')
        _mock_settings = self.__mock_settings.start()
        _mock_settings.SECRET_KEY = 'secret'
        self.__subject = TokenGenerator(_Tokenable(token_hash='hello'), 'token_hash')

    def test_generates_an_appropriate_token(self):
        self.assertEqual('f15f486e6d87d4250297', self.__subject.generate())

    @mock.patch('pyeti.eti_django.tokens.crypto')
    def test_uses_correct_parts_to_construct_token(self, mock_crypto):
        self.__subject.generate()
        mock_crypto.salted_hmac.assert_called_once_with(  # noqa: S106
            '%s._Tokenable' % self.__class__.__module__,
            'hello',
            secret='secret'
        )

    def test_is_callable(self):
        self.assertEqual(self.__subject(), self.__subject.generate())

    def test_validates_other_tokens(self):
        self.assertTrue(self.__subject.validate(self.__subject.generate()))
        self.assertFalse(self.__subject.validate('invalid_token'))

    @mock.patch('pyeti.eti_django.tokens.crypto')
    def test_validates_securely(self, mock_crypto):
        token = faker.word()
        self.__subject.validate(token)
        mock_crypto.constant_time_compare.assert_called_once_with(
            self.__subject(), token
        )

    def tearDown(self):
        self.__mock_settings.stop()
        super().tearDown()


class HasSecureTokenMixinTests(TestCase):

    def setUp(self):
        super().setUp()
        self.__subject = _Tokenable()

    def test_adds_a_token_property(self):
        self.assertIsInstance(self.__subject.token, TokenGenerator)

    def test_generates_a_token_hash_on_save(self):
        self.assertFalse(self.__subject.token_hash)
        try:
            self.__subject.save()
        except OperationalError:
            # Table doesn't exist, just move on.
            pass
        self.assertIsInstance(self.__subject.token_hash, str)
        self.assertEqual(len(self.__subject.token_hash), 16)

    def test_does_not_override_existing_token_hash(self):
        self.__subject.token_hash = 'hello'
        try:
            self.__subject.save()
        except OperationalError:
            # Table doesn't exist, just move on.
            pass
        self.assertEqual(self.__subject.token_hash, 'hello')


class _Tokenable(HasSecureTokenMixin, models.Model):

    class Meta:
        app_label = 'pyeti.eti_django'
