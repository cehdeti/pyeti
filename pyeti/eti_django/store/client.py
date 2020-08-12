import logging

import requests
from django.conf import settings

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

    def subscription(self, user_id, registration_code, show_details=False, **params):
        path = 'account_subscriptions'
        if user_id:
            path += '/%s' % user_id
        return self._do_request(path, params=self._params(
            registration_code=registration_code,
            show_details=int(show_details),
            **params
        ))

    def subscriptions_by_user(self, user_id, **params):
        return self._do_json('users/%s/account_subscriptions' % user_id, params=self._params(**params))

    ##########
    # Products
    ##########

    def products(self, **params):
        return self._do_json('products', params=self._params(*params))

    def product(self, pk, **params):
        return self._do_json('products/%s' % pk, params=self._params(**params))

    #######
    # Users
    #######

    def users(self, **params):
        """
        Filters use the `ransack` gem syntax:
        https://github.com/activerecord-hackery/ransack#search-matchers
        """
        return self._do_json('users', params=self._params(**params))

    def user(self, pk, **params):
        return self._do_json('users/%s' % pk, params=self._params(**params))

    def create_user(self, email, password, **data):
        data['email'] = email
        data['password'] = password
        return self._do_json('users', method='post', json={'user': data})

    ########
    # Orders
    ########

    def orders(self, **params):
        return self._do_json('orders', params=self._params(**params))

    def order(self, pk, **params):
        return self._do_json('orders/%s' % pk, params=self._params(**params))

    def orders_by_user(self, user_id, **params):
        return self._do_json('users/%s/orders' % user_id, params=self._params(**params))

    def current_order(self, user_id, **params):
        return self._do_json('orders/current', params=self._params(
            user_id=user_id,
            **params
        ))

    def create_order(self, user_id, email, **data):
        data['user_id'] = user_id
        data['email'] = email
        return self._do_json('orders', method='post', json={'order': data})

    def update_order(self, pk, order_token, line_items):
        return self._do_json(
            'orders/%s' % pk,
            method='put',
            params={'order_token': order_token},
            json=line_items,
        )

    def create_line_item(self, order_id, order_token, product_id, quantity=1, **data):
        data['variant_id'] = product_id
        data['quantity'] = quantity
        return self._do_json(
            'orders/%s/line_items' % order_id,
            method='post',
            params={'order_token': order_token},
            json={'line_item': data},
        )

    ##########
    # Webinars
    ##########

    def webinars(self, **params):
        return self._do_json('webinars/all', params=self._params(**params))

    def webinar(self, pk, **params):
        return self._do_json('webinars/%s' % pk, params=self._params(**params))

    def webinar_registrations(self, **params):
        return self._do_json('webinar_registrations', params=self._params(**params))

    def webinar_registration(self, pk, **params):
        return self._do_json('webinar_registrations/%s' % pk, params=self._params(**params))

    def webinar_registrations_by_user(self, user_id, **params):
        return self._do_json('users/%s/webinar_registrations' % user_id, params=self._params(**params))

    def create_webinar_registration(self, user_id, webinar_id, **data):
        data['user_id'] = user_id
        data['product_id'] = webinar_id
        return self._do_request('webinar_registrations', method='post', json={'webinar_registration': data})

    #########
    # End API
    #########

    def _build_url(self, path):
        return '%s%s' % (self._endpoint, path)

    def _do_request(self, path, method='get', **kwargs):
        kwargs.setdefault('headers', self._headers)
        kwargs.setdefault('timeout', 10)
        kwargs.setdefault('verify', getattr(settings, 'PYETI_STORE_VERIFY_SSL', not settings.DEBUG))
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

    def _params(self, **params):
        if self._group:
            params['group'] = self._group
        return params


store = Store(
    getattr(settings, 'PYETI_STORE_URL', None),
    getattr(settings, 'PYETI_STORE_AUTH_TOKEN', None),
    group=getattr(settings, 'PYETI_STORE_PRODUCT_GROUP', None)
)
