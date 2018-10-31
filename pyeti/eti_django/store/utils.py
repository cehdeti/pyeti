from django.conf import settings
from django.utils import timezone

from dateutil import parser
from datetime import timedelta


parse_spree_date = parser.parse
parse_spree_datetime = parser.parse


def difference_in_days(string):
    return (parse_spree_date(string) - timezone.now()).days


_DEFAULT_SYNC_FREQUENCY = timedelta(days=2)


def get_sync_cutoff():
    """
    Returns a datetime such that any usage licence with a `last_synced_at` value
    less than the returned value is in need of a sync from the store.
    """
    frequency = getattr(
        settings,
        'PYETI_STORE_LICENSE_SYNC_FREQUENCY',
        _DEFAULT_SYNC_FREQUENCY
    )
    return timezone.now() - frequency
