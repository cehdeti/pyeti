from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import (
    get_language_info, gettext as _, gettext_lazy as _l,
)

from pyeti.eti_django.models import KeyedCacheManager


def _default_langcode():
    return settings.LANGUAGE_CODE


class PlaceholderManager(KeyedCacheManager):

    def get_by_natural_key(self, name, langcode):
        return self.get(name=name, langcode=langcode)


class Placeholder(models.Model):

    name = models.CharField(max_length=256)
    langcode = models.CharField(verbose_name=_l('language'), max_length=12, blank=True, default=_default_langcode)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    objects = PlaceholderManager()

    def natural_key(self):
        return (self.name, self.langcode)

    def __str__(self):
        lang = get_language_info(self.langcode)
        return _('%(name)s (%(language)s)') % {
            'name': self.name,
            'language': lang['name_translated'],
        }

    class Meta:
        get_latest_by = 'created_at'
        unique_together = ('name', 'langcode')


@receiver(post_save, sender=Placeholder)
def reset_placeholder_cache(*args, **kwargs):
    Placeholder.objects.cache.reset()
