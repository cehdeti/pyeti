from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _


class SupportConfig(AppConfig):
    name = 'pyeti.eti_django.support'
    verbose_name = _('Support')

    def ready(self):
        if getattr(settings, 'PYETI_SUPPORT_EMAIL', None):
            return
        raise ImproperlyConfigured('You must specify a `PYETI_SUPPORT_EMAIL` setting')
