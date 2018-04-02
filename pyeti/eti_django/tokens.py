from django.conf import settings
from django.db import models
from django.utils import crypto


class TokenGenerator(object):
    """
    A general use token generator and validator. Differs from the
    `PasswordResetTokenGenerator` in Django core in that these tokens do not
    contain explicit expiry times or conditions.

    Relies on an object having an attribute that will be used as the hash value
    for the token. `django.utils.crypto.get_random_string()` would be suitable
    for generating that value that; see `HasSecureTokenMixin` below for an
    example implementation.
    """

    def __init__(self, obj, hash_attribute):
        self.__object = obj
        self.__attribute = hash_attribute

    def generate(self):
        """
        Generates a new signed token for the object.
        """
        return crypto.salted_hmac(
            self.__key_salt,
            getattr(self.__object, self.__attribute),
            secret=settings.SECRET_KEY,
        ).hexdigest()[::2]

    def validate(self, token):
        """
        Validates the given token against the object's token in a
        cryptographically secure way. Returns `True` if they match, `False` if
        not.
        """
        return crypto.constant_time_compare(self.generate(), token)

    def __call__(self):
        return self.generate()

    @property
    def __key_salt(self):
        cls = self.__object.__class__
        return '%s.%s' % (cls.__module__, cls.__name__)


class HasSecureTokenMixin(models.Model):
    """
    Small mixin for models that should have a token attached to them. Usage:

        ```
        from django.db import models
        from django.utils import crypto


        class MyModel(HasSecureTokenMixin, models.Model):
            pass


        record = MyModel.objects.first()
        token = record.token.generate()  # or record.token()
        record.token.validate(other_token)
    """

    token_hash = models.CharField(max_length=16)

    @property
    def token(self):
        return TokenGenerator(self, 'token_hash')

    def save(self, *args, **kwargs):
        if not self.token_hash:
            self.token_hash = crypto.get_random_string(length=16)
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True
