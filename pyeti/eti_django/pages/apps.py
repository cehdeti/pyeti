from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PagesConfig(AppConfig):
    name = 'pyeti.eti_django.pages'
    verbose_name = _('Pages')
    default_auto_field = 'django.db.models.AutoField'
