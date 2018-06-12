from django.dispatch import Signal


no_license_redirect = Signal(providing_args=['request'])
expired_license_redirect = Signal(providing_args=['request'])
