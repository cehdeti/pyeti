from datetime import timedelta
from uuid import uuid4

import factory
from django.utils import timezone

from . import models


class UsageLicenseFactory(factory.django.DjangoModelFactory):

    token = factory.LazyFunction(uuid4)
    num_seats = 10
    start_date = factory.LazyFunction(lambda: timezone.now() - timedelta(days=3650))
    end_date = factory.LazyFunction(lambda: timezone.now() + timedelta(days=3650))

    class Meta:
        model = models.UsageLicense
