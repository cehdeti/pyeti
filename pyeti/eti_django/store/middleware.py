try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:  # pragma: no cover
    MiddlewareMixin = object

import re

from django.conf import settings
from django.shortcuts import redirect
from django.utils.functional import cached_property

from . import signals


class SubscriptionMiddleware(MiddlewareMixin):
    """
    Checks the current user's subscription to make sure it is valid.

    Relies on the user model in the request having a `usage_license` attribute;
    whether that is a relation on the user model or just an attribute pointing
    to something else is up to you.

    Signals:
        - `pyeti.eti_django.store.signals.no_license_redirect`: Called when
          redirecting because the user has no license. Includes the `request` as
          an argument.
        - `pyeti.eti_django.store.signals.expired_license_redirect`: Called when
          redirecting because the user has an expired license. Includes the
          `request` as an argument.

    Configuration options:
        - `PYETI_STORE_DISABLE_LICENSE_CHECK`: Whether or not to check for valid
          usage licenses. This effectively disables all limitations based on the
          user having a valid usage license.
        - `PYETI_STORE_NO_LICENSE_REDIRECT`: The path to redirect to when the
          user does not have a usage license. Accepts anything that can be
          passed to `django.shortcuts.redirect`.
        - `PYETI_STORE_EXPIRED_LICENSE_REDIRECT`: The path to redirect to when
          the user has an expired license. Accepts anything that can be passed
          to `django.shortcuts.redirect`.
        - `PYETI_STORE_IGNORED_PATHS`: A list of paths and path prefixes that
          do not trigger a check for a valid license.
    """

    def process_request(self, request):
        if request.user.is_anonymous or \
                getattr(settings, 'PYETI_STORE_DISABLE_LICENSE_CHECK', settings.DEBUG) or \
                self.should_ignore(request):
            return

        ulicense = self.get_usage_license(request)

        if not ulicense:
            signals.no_license_redirect.send(sender=self.__class__, request=request)
            return redirect(self.no_license_url)
        if ulicense.is_expired or ulicense.needs_sync:
            ulicense.sync_from_store().save()
        if ulicense.is_expired:
            signals.expired_license_redirect.send(sender=self.__class__, request=request)
            return redirect(self.expired_license_url)

    def should_ignore(self, request):
        """
        Whether or not the subscription should be checked for this request. This
        method could be overridden if your implementation requires something
        more than setting ignored paths.
        """
        return self.__is_ignored_path(request.get_full_path())

    def get_usage_license(self, request):
        """
        Returns the usage license for the current request. This method could be
        overridden if the usage license comes from some place other than the
        current user.
        """
        return request.user.usage_license

    @cached_property
    def no_license_url(self):
        return getattr(settings, 'PYETI_STORE_NO_LICENSE_REDIRECT', '/')

    @cached_property
    def expired_license_url(self):
        return getattr(settings, 'PYETI_STORE_EXPIRED_LICENSE_REDIRECT', '/')

    def __is_ignored_path(self, path):
        ignored_paths = list(getattr(settings, 'PYETI_STORE_IGNORED_PATHS', []))

        ignored_paths.extend([
            '^%s$' % self.no_license_url,
            '^%s$' % self.expired_license_url,
        ])

        for p in ignored_paths:
            if callable(p):
                p = p()
            if re.search(str(p), path):
                return True
        return False
