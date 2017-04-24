from django.core.management.base import BaseCommand

from pyeti.eti_django.assets import download_asset_manifest


class Command(BaseCommand):

    help = 'Refreshes the asset manifest file'

    def handle(self, *args, **options):
        filename = download_asset_manifest(True)
        self.stdout.write(self.style.SUCCESS(
            'Manifest file successfully downloaded to %s' % filename
        ))
