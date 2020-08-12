import factory
from django.conf import settings
from faker import Faker

from . import models

fake = Faker()


class PlaceholderFactory(factory.django.DjangoModelFactory):

    name = factory.Sequence(lambda n: '%s %s' % (fake.word, n))
    langcode = factory.Iterator(settings.LANGUAGES, getter=lambda c: c[0])
    content = factory.Faker('text')

    class Meta:
        model = models.Placeholder
