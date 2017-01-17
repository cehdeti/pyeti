from django.conf import settings
from django import template
import os
import requests
import shutil
import json


register = template.Library()

if hasattr(settings, 'ASSET_MANIFEST_FILENAME'):
    _asset_manifest_filename = settings.ASSET_MANIFEST_FILENAME
else:
    _asset_manifest_filename = 'rev-manifest.json'


def _asset_url(name):
    url = os.path.join(settings.STATIC_URL, name)
    if url.startswith('/'):
        url = 'http://localhost:8000%s' % url
    return url


def _get_asset_map():
    filename = os.path.join(settings.BASE_DIR, _asset_manifest_filename)

    if settings.DEBUG or not os.path.isfile(filename):
        response = requests.get(_asset_url(_asset_manifest_filename), stream=True)
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

    with open(filename) as f:
        return json.loads(f.read())


@register.simple_tag
def hashed_static(name):
    asset_map = _get_asset_map()
    return _asset_url(asset_map[name])
