from django.dispatch import Signal

no_license_redirect = Signal(['request'])
expired_license_redirect = Signal(['request'])
