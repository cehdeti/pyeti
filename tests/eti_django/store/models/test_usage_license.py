from datetime import timedelta
from unittest import mock

import dateutil.parser
from django.test import TestCase, override_settings
from django.utils import timezone
from faker import Faker

from pyeti.eti_django.store.client import (
    NO_SUBSCRIPTION_STATUS_CODE, SUBSCRIPTION_OK_STATUS_CODE,
)
from pyeti.eti_django.store.exceptions import SubscriptionDoesNotExist
from pyeti.eti_django.store.factories import UsageLicenseFactory

_faker = Faker()


class NeedsSyncTests(TestCase):

    def setUp(self):
        super().setUp()
        self.__subject = UsageLicenseFactory.build()

    @override_settings(PYETI_STORE_LICENSE_SYNC_FREQUENCY=timedelta(days=10))
    def test_is_configurable(self):
        self.__subject.last_synced_at = timezone.now() - timedelta(days=8)
        self.assertFalse(self.__subject.needs_sync)
        self.__subject.last_synced_at = timezone.now() - timedelta(days=11)
        self.assertTrue(self.__subject.needs_sync)

    def test_defaults_to_every_2_days(self):
        self.__subject.last_synced_at = timezone.now()
        self.assertFalse(self.__subject.needs_sync)
        self.__subject.last_synced_at = timezone.now() - timedelta(days=3)
        self.assertTrue(self.__subject.needs_sync)


class IsExpiredTests(TestCase):

    def setUp(self):
        super().setUp()
        self.__subject = UsageLicenseFactory.build()

    def test_returns_whether_the_license_is_expired(self):
        self.__subject.end_date = timezone.now() + timedelta(days=1)
        self.assertFalse(self.__subject.is_expired)
        self.__subject.end_date = timezone.now() - timedelta(days=1)
        self.assertTrue(self.__subject.is_expired)


class SyncFromStoreTests(TestCase):

    def setUp(self):
        super().setUp()
        self.__subject = UsageLicenseFactory.build()
        self.__store = mock.Mock()
        self.__subscription = {
            'num_seats': _faker.pyint(),
            'start': _faker.iso8601(),
            'end': _faker.iso8601(),
            'order_number': _faker.pyint(),
        }
        response = mock.Mock()
        response.json.return_value = self.__subscription
        self.__store.subscription.return_value = response

    def test_sets_attributes_from_the_subscription(self):
        self.__subject.sync_from_store(self.__store)
        self.assertEqual(self.__subject.num_seats, self.__subscription['num_seats'])
        self.assertEqual(self.__subject.spree_order_number, self.__subscription['order_number'])
        self.assertEqual(self.__subject.start_date, dateutil.parser.parse(self.__subscription['start']))
        self.assertEqual(self.__subject.end_date, dateutil.parser.parse(self.__subscription['end']))

    def test_returns_the_object(self):
        self.assertIs(
            self.__subject,
            self.__subject.sync_from_store(self.__store)
        )

    def test_sets_the_last_synced_at_property(self):
        then = timezone.now()
        self.__subject.last_synced_at = then
        self.__subject.sync_from_store(self.__store)
        self.assertGreater(self.__subject.last_synced_at, then)

    @mock.patch('pyeti.eti_django.store.models.main_store')
    def test_uses_globally_configured_store_if_none_is_provided(self, mock_store):
        response = mock.Mock()
        response.status_code = SUBSCRIPTION_OK_STATUS_CODE
        mock_store.subscription.return_value = response
        try:
            self.__subject.sync_from_store()
        except Exception:  # noqa: S110
            pass
        mock_store.subscription.assert_called_once_with(mock.ANY, mock.ANY, show_details=mock.ANY)

    def test_raises_if_the_subscription_does_not_exist(self):
        response = mock.Mock()
        response.status_code = NO_SUBSCRIPTION_STATUS_CODE
        self.__store.subscription.return_value = response
        self.assertRaises(SubscriptionDoesNotExist, self.__subject.sync_from_store, self.__store)


class StoreOrderLinkTests(TestCase):

    def setUp(self):
        super().setUp()
        self.__subject = UsageLicenseFactory.build()

    @override_settings(PYETI_STORE_URL='https://example.com/')
    def test_returns_the_correct_url(self):
        self.__subject.spree_order_number = 10
        self.assertEqual('https://example.com/orders/10/', self.__subject.store_order_link)

    def test_returns_none_if_there_is_no_order_number(self):
        self.__subject.spree_order_number = None
        self.assertIsNone(self.__subject.store_order_link)

    def test_returns_none_if_no_url_is_configured(self):
        self.__subject.spree_order_number = _faker.pyint()
        self.assertIsNone(self.__subject.store_order_link)


class StringTests(TestCase):

    def setUp(self):
        super().setUp()
        self.__subject = UsageLicenseFactory.build()

    def test_returns_a_reasonable_string_representation(self):
        self.__subject.token = _faker.uuid4()
        self.assertIn(self.__subject.token, str(self.__subject))
