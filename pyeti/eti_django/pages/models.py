from django.db import models
from django.conf import settings
from django.utils.translation import get_language_info, ugettext as _, ugettext_lazy as _l

from pyeti.eti_django.models import KeyedCacheManager


class Placeholder(models.Model):

    name = models.CharField(max_length=256)
    langcode = models.CharField(verbose_name=_l('language'), max_length=12, blank=True, default=settings.LANGUAGE_CODE)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    objects = KeyedCacheManager(cache_key=('name', 'langcode'))

    def __str__(self):
        lang = get_language_info(self.langcode)
        return _('%(name)s (%(language)s)') % {
            'name': self.name,
            'language': lang['name_translated'],
        }

    class Meta:
        get_latest_by = 'created_at'
        unique_together = ('name', 'langcode')
