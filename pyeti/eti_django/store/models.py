from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from django.utils import timezone

from datetime import timedelta

from .client import store as main_store, NO_SUBSCRIPTION_STATUS_CODE
from .exceptions import SubscriptionDoesNotExist
from .utils import parse_spree_date


class UsageLicenseQuerySet(models.QuerySet):

    def expired(self):
        return self.filter(end_date__lt=timezone.now().date())


class UsageLicense(models.Model):
    """
    Represents the ability to use the app for a certain period of time.
    Essentially a local cache of a subscription from the store.
    """

    DEFAULT_SYNC_FREQUENCY = timedelta(days=2)

    token = models.CharField(max_length=64, unique=True)
    num_seats = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    last_synced_at = models.DateTimeField(auto_now_add=True)
    spree_order_number = models.CharField(max_length=16, blank=True, null=True)

    objects = UsageLicenseQuerySet.as_manager()

    @property
    def store_order_link(self):
        if self.spree_order_number is None:
            return
        store_host = getattr(settings, 'PYETI_STORE_URL', None)
        if store_host is None:
            return
        return '%sorders/%s/' % (store_host, self.spree_order_number)

    @property
    def is_expired(self):
        return self.end_date < timezone.now().date()

    @property
    def needs_sync(self):
        """
        Determines whether or not this license needs to be synced from the
        store.

        Set the sync frequency with the `PYETI_STORE_LICENSE_SYNC_FREQUENCY`
        setting. Accepts a `timedelta` object.
        """
        frequency = getattr(
            settings,
            'PYETI_STORE_LICENSE_SYNC_FREQUENCY',
            self.DEFAULT_SYNC_FREQUENCY
        )
        return self.last_synced_at <= (timezone.now() - frequency)

    def sync_from_store(self, store=None):
        """
        Fetches the corresponding subscription from the store and saves its
        attributes on this object. Note that this method does not call `save` on
        the object.
        """
        if store is None:
            store = main_store

        response = store.subscription(None, self.token, show_details=True)

        if response.status_code == NO_SUBSCRIPTION_STATUS_CODE:
            raise SubscriptionDoesNotExist(
                'Could not find subscription with token %s' % self.token
            )

        subscription = response.json()
        self.num_seats = subscription['num_seats']
        self.start_date = parse_spree_date(subscription['start'])
        self.end_date = parse_spree_date(subscription['end'])
        self.spree_order_number = subscription['order_number']
        self.last_synced_at = timezone.now()
        return self

    def __str__(self):
        return _('Registration token %(token)s) ') % {'token': self.token}
