from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from pyeti.eti_django.pages.models import Placeholder

register = template.Library()


@register.simple_tag(takes_context=True)
def placeholder(context, key, language=None):
    """
    Returns the text for a given placeholder in the given language. If a
    placeholder for the given key does not exist, returns an empty string. If a
    language is not specified, use `request.LANGUAGE_CODE` or
    `settings.LANGUAGE_CODE`.
    """
    if language:
        pass
    elif hasattr(context['request'], 'LANGUAGE_CODE'):
        language = context['request'].LANGUAGE_CODE
    elif hasattr(settings, 'LANGUAGE_CODE'):
        language = settings.LANGUAGE_CODE

    placeholder = Placeholder.objects.cache.get((key, language))
    return mark_safe(placeholder.content) if placeholder else ''  # noqa: S308,S703
