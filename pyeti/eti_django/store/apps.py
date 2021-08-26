from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StoreConfig(AppConfig):
    name = 'pyeti.eti_django.store'
    verbose_name = _('Store')
    default_auto_field = 'django.db.models.AutoField'
