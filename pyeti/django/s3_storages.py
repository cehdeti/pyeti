"""
Defines Django storage backends that use S3 configured via Django settings.
"""
from storages.backends.s3boto import S3BotoStorage
from django.conf import settings


class StaticStorage(S3BotoStorage):
    location = settings.STATIC_DIR


class MediaStorage(S3BotoStorage):
    location = settings.MEDIA_DIR
