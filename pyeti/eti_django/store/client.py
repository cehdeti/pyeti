from django.conf import settings

import requests
import logging


requests.packages.urllib3.disable_warnings()

logger = logging.getLogger(__name__)


SUBSCRIPTION_OK_STATUS_CODE = 200
LAPSED_SUBSCRIPTION_STATUS_CODE = 211
NO_SUBSCRIPTION_STATUS_CODE = 212


class Store(object):

    def __init__(self, url, token, group=None):
        self._endpoint = '%sapi/v1/' % url
        self._headers = {
            'X-Spree-Token': token,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        self._group = group

    ###########
    # Begin API
    ###########

    ###############
    # Subscriptions
    ###############

    def subscription(self, user_id, registration_code, show_details=False):
        path = 'account_subscriptions'
        if user_id:
            path += '/%s' % user_id
        params = {
            'registration_code': registration_code,
            'show_details': int(show_details),
        }
        if self._group:
            params['group'] = self._group
        return self._do_request(path, params=params)

    def subscriptions_by_user(self, user_id):
        params = {}
        if self._group:
            params['group'] = self._group
        return self._do_json('users/%s/account_subscriptions' % user_id, params=params)

    ##########
    # Products
    ##########

    def products(self):
        return self._do_json('products')

    def product(self, pk):
        return self._do_json('products/%s' % pk)

    #######
    # Users
    #######

    def users(self):
        return self._do_json('users')

    def user(self, pk):
        return self._do_json('users/%s' % pk)

    def create_user(self, email, password, **kwargs):
        data = {'user[%s]' % k: v for k, v in kwargs.items()}
        data['user[email]'] = email
        data['user[password]'] = password
        return self._do_json('users', method='post', data=data)

    ########
    # Orders
    ########

    def orders(self):
        return self._do_json('orders')

    def order(self, pk):
        return self._do_json('orders/%s' % pk)

    def orders_by_user(self, user_id):
        return self._do_json('users/%s/orders' % user_id)

    def current_order(self, user_id):
        return self._do_json('orders/current', params={'user_id': user_id})

    def create_order(self, user_id, email, **kwargs):
        data = {'order[%s]' % k: v for k, v in kwargs.items()}
        data['order[user_id]'] = user_id
        data['order[email]'] = email
        return self._do_json('orders', method='post', data=data)

    def update_order(self, pk, order_token, line_items):
        return self._do_json(
            'orders/%s' % pk,
            method='put',
            params={'order_token': order_token},
            data=line_items,
        )

    def create_line_item(self, order_id, order_token, product_id, quantity=1, **kwargs):
        data = {'line_item[%s]' % k: v for k, v in kwargs.items()}
        data['line_item[variant_id]'] = product_id
        data['line_item[quantity]'] = quantity
        return self._do_json(
            'orders/%s/line_items' % order_id,
            method='post',
            params={'order_token': order_token},
            data=data,
        )

    ##########
    # Webinars
    ##########

    def webinars(self):
        return self._do_json('webinars/all')

    def webinar(self, pk):
        return self._do_json('webinars/%s' % pk)

    def webinar_registrations(self):
        return self._do_json('webinar_registrations')

    def webinar_registration(self, pk):
        return self._do_json('webinar_registrations/%s' % pk)

    def webinar_registrations_by_user(self, user_id):
        return self._do_json('users/%s/webinar_registrations' % user_id)

    def create_webinar_registration(self, user_id, webinar_id, **kwargs):
        data = {'webinar_registration[%s]' % k: v for k, v in kwargs.items()}
        data['webinar_registration[user_id]'] = user_id
        data['webinar_registration[product_id]'] = webinar_id
        return self._do_json('webinar_registrations', method='post', data=data)

    #########
    # End API
    #########

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
    getattr(settings, 'PYETI_STORE_AUTH_TOKEN', None),
    group=getattr(settings, 'PYETI_STORE_PRODUCT_GROUP', None)
)
