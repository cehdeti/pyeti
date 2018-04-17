from django.db import models


class KeyedModelCache(object):
    """
    A cache for model records keyed by a specific field. Cache key may be one of
    the following:
        - `string`: The name of a property on the model.
        - `tuple`: A tuple of model property names.
    If no cache key is specified and the model defines a `natural_key` method,
    the return value of that method will be used as cache keys. Otherwise, the
    `pk` will be used.

    Note that you probably will not use this class directly. Rather, use it
    through the `KeyedCacheManager` object.

    It's also worth noting that this class will load and store *ALL* of the
    records for your given model from the database, so only use this tools on
    recordsets that will stay relatively small.
    """

    def __init__(self, queryset, cache_key=None):
        self.__queryset = queryset
        if cache_key is not None and not isinstance(cache_key, tuple):
            self.__key = (cache_key,)
        else:
            self.__key = cache_key
        self.__cache = None

    def get(self, key):
        if self.__cache is None:
            self.__load()
        if not isinstance(key, tuple):
            key = (key,)
        return self.__cache.get(key)

    def reset(self):
        self.__cache = None
        return self

    def __load(self):
        self.__cache = {self.__get_key(o): o for o in self.__queryset.all()}

    def __get_key(self, record):
        if self.__key:
            return tuple(getattr(record, attr) for attr in self.__key)
        if hasattr(record, 'natural_key'):
            return record.natural_key()
        return (record.pk,)


class KeyedCacheManager(models.Manager):
    """
    Model manager that supports fetching items from a cache by a given field.
    Use as follows:

        ```
        class MyModel(models.Model):

            objects = KeyedCacheManager(cache_key='some_attr')


        MyModel.objects.cache.get('value')
        MyModel.objects.cache.reset()
        ```
    """

    def __init__(self, *args, cache_key=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = KeyedModelCache(self, cache_key=cache_key)
