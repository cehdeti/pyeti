import random
from collections import namedtuple
from unittest import TestCase, mock

from faker import Faker

from pyeti.eti_django.models import KeyedCacheManager, KeyedModelCache

faker = Faker()
srandom = random.SystemRandom()


_SingleKeyCachableObject = namedtuple('_KeyCachableObject', ['key'])
_TupleKeyCachableObject = namedtuple('_KeyCachableObject', ['key_1', 'key_2'])
_PkCachableObject = namedtuple('_PkCachableObject', ['pk'])


class _NaturalKeyCachableObject(object):

    def __init__(self, key):
        self.key = key

    def natural_key(self):
        return (self.key,)


def _mock_queryset(records):
    queryset = mock.Mock()
    queryset.all.return_value = records
    return queryset


class KeyedModelCacheWithStringCacheKeyTests(TestCase):

    def setUp(self):
        super().setUp()

        self.__records = [
            _SingleKeyCachableObject(faker.word()),
            _SingleKeyCachableObject(faker.word()),
            _SingleKeyCachableObject(faker.word())
        ]
        self.__queryset = _mock_queryset(self.__records)
        self.__subject = KeyedModelCache(self.__queryset, cache_key='key')

    def test_getting_a_record_by_key_returns_the_record(self):
        index = srandom.randint(0, len(self.__records) - 1)
        self.assertIs(
            self.__subject.get(self.__records[index].key),
            self.__records[index]
        )

    def test_getting_a_record_that_doesnt_exist_returns_none(self):
        self.assertIsNone(self.__subject.get(faker.word()))

    def test_does_not_evaluate_the_queryset_until_gotten(self):
        self.assertFalse(self.__queryset.all.called)
        self.__subject.get(faker.word())
        self.assertTrue(self.__queryset.all.called)


class KeyedModelCacheWithTupleCacheKeyTests(TestCase):

    def setUp(self):
        super().setUp()

        self.__records = [
            _TupleKeyCachableObject(faker.word(), faker.word()),
            _TupleKeyCachableObject(faker.word(), faker.word()),
            _TupleKeyCachableObject(faker.word(), faker.word())
        ]
        self.__queryset = _mock_queryset(self.__records)
        self.__subject = KeyedModelCache(self.__queryset, cache_key=('key_1', 'key_2'))

    def test_getting_a_record_by_key_returns_the_record(self):
        index = srandom.randint(0, len(self.__records) - 1)
        record = self.__records[index]
        self.assertIs(
            self.__subject.get((record.key_1, record.key_2)),
            self.__records[index]
        )

    def test_getting_a_record_that_doesnt_exist_returns_none(self):
        self.assertIsNone(self.__subject.get((faker.word(), faker.word())))


class KeyedModelCacheWithNaturalKeyTests(TestCase):

    def setUp(self):
        super().setUp()

        self.__records = [
            _NaturalKeyCachableObject(faker.word()),
            _NaturalKeyCachableObject(faker.word()),
            _NaturalKeyCachableObject(faker.word())
        ]
        self.__queryset = _mock_queryset(self.__records)
        self.__subject = KeyedModelCache(self.__queryset)

    def test_getting_a_record_by_key_returns_the_record(self):
        index = srandom.randint(0, len(self.__records) - 1)
        record = self.__records[index]
        self.assertIs(
            self.__subject.get((record.key,)),
            self.__records[index]
        )

    def test_getting_a_record_that_doesnt_exist_returns_none(self):
        self.assertIsNone(self.__subject.get((faker.word(),)))


class KeyedModelCacheWithPkKeyTests(TestCase):

    def setUp(self):
        super().setUp()

        self.__records = [
            _PkCachableObject(faker.pyint()),
            _PkCachableObject(faker.pyint()),
            _PkCachableObject(faker.pyint())
        ]
        self.__queryset = _mock_queryset(self.__records)
        self.__subject = KeyedModelCache(self.__queryset)

    def test_getting_a_record_by_pk_returns_the_record(self):
        index = srandom.randint(0, len(self.__records) - 1)
        self.assertIs(
            self.__subject.get(self.__records[index].pk),
            self.__records[index]
        )

    def test_getting_a_record_that_doesnt_exist_returns_none(self):
        self.assertIsNone(self.__subject.get(faker.word()))


class KeyedModelCacheResetTests(TestCase):

    def setUp(self):
        super().setUp()

        self.__queryset = _mock_queryset([])
        self.__subject = KeyedModelCache(self.__queryset)

    def test_resetting_refreshes_the_queryset_on_the_next_get(self):
        self.__subject.get(faker.word())
        self.__subject.get(faker.word())
        self.__subject.reset()
        self.__subject.get(faker.word())
        self.assertEqual(2, self.__queryset.all.call_count)


class KeyedCacheManagerTests(TestCase):

    def setUp(self):
        self.__records = [
            _SingleKeyCachableObject(faker.word()),
            _SingleKeyCachableObject(faker.word()),
            _SingleKeyCachableObject(faker.word())
        ]
        self.__subject = KeyedCacheManager(cache_key='key')
        self.__subject.all = mock.Mock(return_value=self.__records)

    def test_sets_a_cache_object_to_the_cache_property(self):
        self.assertIsInstance(self.__subject.cache, KeyedModelCache)

    def test_passes_the_cache_key_to_the_cache_object(self):
        index = srandom.randint(0, len(self.__records) - 1)
        self.assertIs(
            self.__subject.cache.get(self.__records[index].key),
            self.__records[index]
        )

    def test_queries_self_in_the_cache(self):
        self.__subject.cache.get(faker.word())
        self.assertTrue(self.__subject.all.called)
