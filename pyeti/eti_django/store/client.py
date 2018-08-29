from django.conf import settings

import requests
import logging


requests.packages.urllib3.disable_warnings()

logger = logging.getLogger(__name__)


SUBSCRIPTION_OK_STATUS_CODE = 200
LAPSED_SUBSCRIPTION_STATUS_CODE = 211
NO_SUBSCRIPTION_STATUS_CODE = 212


class Store():

    def __init__(self, url, token):
        self._endpoint = '%sapi/v1/' % url
        self._headers = {
            'X-Spree-Token': token,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def subscription(self, user_id, registration_code, show_details=False):
        path = 'account_subscriptions'
        if user_id:
            path += '/%s' % user_id
        return self._do_request(path, params={
            'registration_code': registration_code,
            'show_details': int(show_details),
        })

    def products(self):
        return self._do_json('products')

    def product(self, pk):
        return self._do_json('products/%s' % pk)

    def users(self):
        return self._do_json('users')

    def user(self, pk):
        return self._do_json('users/%s' % pk)

    def orders(self):
        return self._do_json('orders')

    def order(self, pk):
        return self._do_json('orders/%s' % pk)

    def user_orders(self, user_id):
        return self._do_json('users/%s/orders' % user_id)

    def _build_url(self, path):
        return '%s%s' % (self._endpoint, path)

    def _do_request(self, path, method='get', **kwargs):
        kwargs.setdefault('headers', self._headers)
        kwargs.setdefault('timeout', 10)
        kwargs.setdefault('verify', not settings.DEBUG)
        return requests.request(method, self._build_url(path), **kwargs)

    def _do_json(self, *args, **kwargs):
        response = self._do_request(*args, **kwargs)

        try:
            return response.json()
        except Exception as e:
            logger.error("""
                error calling api:
                URL: %s
                result: %s
                result status %s
                could not decode result json: %s
            """ % (response.url, response.text, response.status_code, e))


store = Store(
    getattr(settings, 'PYETI_STORE_URL', None),
    getattr(settings, 'PYETI_STORE_AUTH_TOKEN', None)
)
