import os

from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage


class S3StaticStorage(S3Boto3Storage):
    querystring_auth = False
    bucket_name = '%s-public' % os.environ.get('S3_BUCKET_NAME')
    location = 'assets'
    preload_metadata = True
    default_acl = 'public-read'


class S3PublicMediaStorage(S3Boto3Storage):
    querystring_auth = False
    bucket_name = '%s-public' % os.environ.get('S3_BUCKET_NAME')
    location = 'uploads'
    default_acl = 'public-read'


class S3PrivateMediaStorage(S3Boto3Storage):
    bucket_name = '%s-private' % os.environ.get('S3_BUCKET_NAME')


class PrivateFileSystemStorage(FileSystemStorage):
    location = 'private'


def private_media_storage():
    """
    This can be used as a `storage` option in `FileField`s and `ImageField`s
    that need to contain files that are only visible via expiring URL.

        ```
        from core.storages import private_media_storage


        class MyModel(models.Model):

            private_file = models.FileField(storage=private_media_storage)
        ```

    Locally, we just use a `private` directory on the filesystem. On AWS, we
    use a private S3 bucket.
    """
    if 'S3_BUCKET_NAME' in os.environ:
        return S3PrivateMediaStorage()
    return PrivateFileSystemStorage()
