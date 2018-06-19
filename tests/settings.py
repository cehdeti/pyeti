SECRET_KEY = 'NOTASECRET'


INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',

    'pyeti.eti_django',
    'pyeti.eti_django.store',
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}


ROOT_URLCONF = 'tests.urls'
