from unittest import mock

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse, reverse_lazy

from pyeti.eti_django.store.middleware import SubscriptionMiddleware


@override_settings(
    PYETI_STORE_DISABLE_LICENSE_CHECK=False,
    PYETI_STORE_IGNORED_PATHS=[
        '^/ignored$',
        lambda: '^/also-ignored$',
    ],
)
class SubscriptionMiddlewareTests(TestCase):

    def setUp(self):
        super().setUp()
        SubscriptionMiddleware.expired_license_url = reverse('expired_license')
        SubscriptionMiddleware.no_license_url = reverse_lazy('no_license')
        self.__subject = SubscriptionMiddleware().process_request
        self.__factory = RequestFactory()
        self.__request = self.__factory.get('/')
        self.__request.user = User()

    def test_allows_unexpired_licenses_through(self):
        ulicense = mock.Mock()
        ulicense.is_expired = False
        ulicense.needs_sync = False
        self.__request.user.usage_license = ulicense
        self.assertIsNone(self.__subject(self.__request))

    def test_redirects_if_there_is_no_usage_license(self):
        self.__request.user.usage_license = None
        response = self.__subject(self.__request)
        self.assertRedirects(response, '/no-license/', fetch_redirect_response=False)

    @mock.patch('pyeti.eti_django.store.middleware.signals')
    def test_signals_if_there_is_no_usage_license(self, mock_signals):
        self.__request.user.usage_license = None
        self.__subject(self.__request)
        mock_signals.no_license_redirect.send.assert_called_once_with(
            sender=SubscriptionMiddleware,
            request=self.__request,
        )

    def test_redirects_if_the_usage_license_is_expired(self):
        ulicense = mock.Mock()
        ulicense.is_expired = True
        ulicense.sync_from_store.return_value = ulicense
        self.__request.user.usage_license = ulicense
        response = self.__subject(self.__request)
        self.assertRedirects(response, '/expired-license/', fetch_redirect_response=False)

    @mock.patch('pyeti.eti_django.store.middleware.signals')
    def test_signals_if_the_usage_license_is_expired(self, mock_signals):
        ulicense = mock.Mock()
        ulicense.is_expired = True
        ulicense.sync_from_store.return_value = ulicense
        self.__request.user.usage_license = ulicense
        self.__subject(self.__request)
        mock_signals.expired_license_redirect.send.assert_called_once_with(
            sender=SubscriptionMiddleware,
            request=self.__request,
        )

    def test_syncs_the_usage_license_if_its_expired(self):
        ulicense = mock.Mock()
        ulicense.is_expired = True
        ulicense.sync_from_store.return_value = ulicense
        self.__request.user.usage_license = ulicense
        self.__subject(self.__request)
        ulicense.sync_from_store.assert_called_once_with()
        ulicense.save.assert_called_once_with()

    def test_syncs_the_usage_license_if_it_needs_a_sync(self):
        ulicense = mock.Mock()
        ulicense.is_expired = False
        ulicense.needs_sync = True
        ulicense.sync_from_store.return_value = ulicense
        self.__request.user.usage_license = ulicense
        self.__subject(self.__request)
        ulicense.sync_from_store.assert_called_once_with()
        ulicense.save.assert_called_once_with()

    def test_does_not_sync_if_not_needed(self):
        ulicense = mock.Mock()
        ulicense.is_expired = False
        ulicense.needs_sync = False
        ulicense.sync_from_store.return_value = ulicense
        self.__request.user.usage_license = ulicense
        self.__subject(self.__request)
        ulicense.sync_from_store.assert_not_called()
        ulicense.save.assert_not_called()

    def test_expired_licenses_can_become_valid_again(self):
        ulicense = mock.Mock()
        ulicense.is_expired = True
        ulicense.needs_sync = False

        def _do_sync():
            ulicense.is_expired = False
            return ulicense

        def _do_save():
            if not ulicense.is_expired:
                return
            raise Exception('Usage license did not save its expiry status')

        ulicense.sync_from_store.side_effect = _do_sync
        ulicense.save.side_effect = _do_save
        self.__request.user.usage_license = ulicense
        self.assertIsNone(self.__subject(self.__request))

    def test_valid_licenses_can_become_expired_again(self):
        ulicense = mock.Mock()
        ulicense.is_expired = False
        ulicense.needs_sync = True

        def _do_sync():
            ulicense.is_expired = True
            return ulicense

        def _do_save():
            if ulicense.is_expired:
                return
            raise Exception('Usage license did not save its expiry status')

        ulicense.sync_from_store.side_effect = _do_sync
        ulicense.save.side_effect = _do_save
        self.__request.user.usage_license = ulicense

        response = self.__subject(self.__request)
        self.assertRedirects(response, '/expired-license/', fetch_redirect_response=False)

    def test_returns_for_anonymous_users(self):
        self.__request.user = AnonymousUser()
        self.assertIsNone(self.__subject(self.__request))

    @override_settings(PYETI_STORE_DISABLE_LICENSE_CHECK=True, DEBUG=False)
    def test_returns_if_license_checks_are_disabled(self):
        self.assertIsNone(self.__subject(self.__request))

    def test_returns_if_the_path_is_ignored(self):
        for path in ['/ignored', '/also-ignored']:
            request = self.__factory.get(path)
            request.user = User()
            self.assertIsNone(self.__subject(request))
