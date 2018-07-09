from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PagesConfig(AppConfig):
    name = 'pyeti.eti_django.pages'
    verbose_name = _('Pages')
