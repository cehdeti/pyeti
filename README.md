# pyeti

A Python package of awesome stuff.

[![Run Status](https://api.shippable.com/projects/5ab54a45f488d607007cad93/badge?branch=master)](https://app.shippable.com/github/cehdeti/pyeti)
[![Coverage Badge](https://api.shippable.com/projects/5ab54a45f488d607007cad93/coverageBadge?branch=master)](https://app.shippable.com/github/cehdeti/pyeti)

## Install

`pip install pyeti` or `pip install -e 'git+https://github.com/cehdeti/pyeti.git@master#egg=pyeti'`

## Usage

### CLI

```
from pyeti.cli import confirm

result = confirm('Do you really want to hurt me? [y/N]', default=False)
```

### Utils

```
from pyeti.utils import empty_context as no_transaction

with transaction.atomic() if transact else no_transaction():
    ...

from pyeti.utils import ignore_exception

@ignore_exception(KeyError)
def get_my_key():
    return hello['my_key']
```

### Pages

The `pyeti.eti_django.pages` module implements some of the more useful features
from the `django-page-cms` library, without all of the unnecessary URL routing
and other features. It allows you do define `{% placeholder %}` areas in your
templates, and provides an admin interface for admins to specify content for
them. First, add this to your `settings.py`:

```
INSTALLED_APPS = [
  ...
  'pyeti.eti_django.pages',
  ...
]
```

Then do `python manage.py migrate`. Then, you can define placeholders in your
templates like this:

```
{% load placeholder %}

<div>
<h1>My Page</h1>

{% placeholder "My Page Content" %}
```

The `{% placeholder %}` tag accepts an optional second parameter for the
language to get content for. If it's omitted, the language from the current
request or the globally-configured language is used, respectively. You will
most likely never need to specify this if you're doing i18n correctly.

Also, you can configure the form widget that is used when admins edit
placeholder content using the `PYETI_PAGES_CONTENT_WIDGET` setting. It should
be a fully-qualified python class. For example, to use a CKEditor widget,
install `django-ckeditor` and set `PYETI_PAGES_CONTENT_WIDGET` to `ckeditor.widgets.CKEditorWidget`.

Also note that this module probably will not play nicely with
`django-page-cms`, since they define the same template tags, use similar
database tables, etc.

### Store

The `pyeti.eti_django.store` module is a library you can use to communicate
with the ETI store and sync/check app subscriptions. To use it, add the
following to your `settings.py`:

```
INSTALLED_APPS = [
  ...
  'pyeti.eti_django.store',
  ...
]

MIDDLEWARE = [
  ...
  'pyeti.eti_django.store.middleware.SubscriptionMiddleware',
  ...
]
```

Then, in a model, add a reference to the `UsageLicense` model. Where you do
this depends on your app.

```
from pyeti.eti_django.store.models import UsageLicense


class Organization(models.Model):

    ...
    usage_license = models.OneToOneField(UsageLicense, models.SET_NULL, blank=True, null=True)
    ...
```

The middleware relies on getting a `UsageLicense` object somehow, either from
the current user (`request.user.usage_license`, by default) or from some other
source. You can subclass `SubscriptionMiddleware` and fetch the usage license
in another way if you need to.

Also included is a Django admin implementation, but you need to wire it up in
your app.

````
from django.contrib import admin

from pyeti.eti_django.store.admin import UsageLicenseAdmin
from pyeti.eti_django.store.models import UsageLicense

admin.site.register(UsageLicense, UsageLicenseAdmin)
````

Possible configuration options are:

* `PYETI_STORE_URL`: The URL of the store
* `PYETI_STORE_AUTH_TOKEN`: The auth token for connecting to the store API
* `PYETI_STORE_PRODUCT_GROUP`: (optional) The name of the product group in the store to
    restrict product and subscription listings by
* `PYETI_STORE_DISABLE_LICENSE_CHECK`: (default: `settings.DEBUG`) A boolean indicating whether licence
    checks should happen. Useful for local development and testing.
* `PYETI_STORE_IGNORED_PATHS`: A list of regexps to check the current path
    against to determine if a license should be required.
* `PYETI_STORE_NO_LICENSE_REDIRECT`: (default: `/`) If no license is found, redirects the user
    to this path. Automatically added to the `PYETI_STORE_IGNORED_PATHS`.
* `PYETI_STORE_EXPIRED_LICENSE_REDIRECT`: (default: `/`) If the user has a licence but it's
    expired, redirect to this path. Automatically added to the
    `PYETI_STORE_IGNORED_PATHS`.
* `PYETI_STORE_LICENSE_SYNC_FREQUENCY`: (default: `timedelta(days=2)`) The frequency with which to sync usage
    licenses from the store. Effectively, the cache lifetime of usage license
    records. Should be a `timedelta` object.
* `PYETI_STORE_USAGE_LICENSE_EXTRA_FIELDS`: (default: `[]`) A list of fields from the store's
    subscription JSON object to store in the `UsageLicense.extra` JSON field.

### Support

The `pyeti.eti_django.support` app includes a form that will create a support
ticket in FreshDesk via email. To use it, add the following to your
`settings.py`:

```
INSTALLED_APPS = [
  ...
  'pyeti.eti_django.support',
  ...
]

PYETI_SUPPORT_FRESHDESK_SUBDOMAIN = 'etiumn'
PYETI_SUPPORT_FRESHDESK_API_KEY = '{your API key}'
PYETI_SUPPORT_FRESHDESK_PRODUCT_ID = '{optional}'
```

Then, import the URL conf if you want to use the package's views and/or
templates.

### Jokes

The cap_second utility will always capitalize the second letter in a python string.

```
from pyeti.jokes import cap_second

string_to_cap_second='Tsthoeu stnahooOTO tnhoustnh'

cap_second(string_to_cap_second)
> 'tSthoeu Stnahoooto Tnhoustnh'

cap_second(string_to_cap_second)
> 'TSthoeu stnahoooto tnhoustnh'
```

## Contributing

* Install dependencies with `make init` (or just `make`).
* We use the built-in `unittest` module for tests, `mock` or mocking, and
  `Faker` for generating dummy data. Run the test suite with `make test`, and
  generate code coverage reports with `make coverage` or `make coverage_html`.
* Code should all follow PEP8 conventions. Check your code style with `make
  lint`.
