import os
import requests
import shutil
import json
from functools import lru_cache
from django.conf import settings


if hasattr(settings, 'ASSET_MANIFEST_FILENAME'):
    _asset_manifest_filename = settings.ASSET_MANIFEST_FILENAME
else:
    _asset_manifest_filename = 'rev-manifest.json'


def asset_url(name):
    url = os.path.join(settings.STATIC_URL, name)
    if url.startswith('/'):
        url = 'http://localhost:8000%s' % url
    return url


def download_asset_manifest(force=False):
    filename = os.path.join(settings.BASE_DIR, _asset_manifest_filename)

    if force or not os.path.isfile(filename):
        response = requests.get(asset_url(_asset_manifest_filename), stream=True)
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

    return filename


_asset_map = None


@lru_cache(maxsize=None)
def get_asset_map():
    with open(download_asset_manifest(settings.DEBUG)) as f:
        return json.loads(f.read())
