from django import template

from pyeti.eti_django.assets import get_asset_map, asset_url


register = template.Library()


@register.simple_tag
def hashed_static(name):
    return asset_url(get_asset_map()[name])
