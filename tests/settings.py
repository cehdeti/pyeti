SECRET_KEY = 'NOTASECRET'  # noqa: S105


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


DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
