SECRET_KEY = 'NOTASECRET'


INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',

    'pyeti.eti_django',
    'pyeti.eti_django.pages',
    'pyeti.eti_django.store',
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pyeti',
    }
}


ROOT_URLCONF = 'tests.urls'
