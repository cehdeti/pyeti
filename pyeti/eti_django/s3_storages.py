from django.conf import settings
from storages.backends.s3boto import S3BotoStorage


class StaticStorage(S3BotoStorage):
    location = settings.STATIC_DIR


class MediaStorage(S3BotoStorage):
    location = settings.MEDIA_DIR
