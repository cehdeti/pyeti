from unittest import TestCase, mock

from faker import Faker
import random

from pyeti.eti_django.db import lock, LOCKS


fake = Faker()
srandom = random.SystemRandom()


class LockTests(TestCase):

    def setUp(self):
        transaction_patcher = mock.patch('pyeti.eti_django.db.transaction')
        self.__transaction = transaction_patcher.start()
        self.addCleanup(transaction_patcher.stop)

        connection_patcher = mock.patch('pyeti.eti_django.db.connection')
        self.__connection = connection_patcher.start()
        self.addCleanup(connection_patcher.stop)

        self.__model = mock.Mock()
        self.__db_table = fake.word()
        self.__model._meta.db_table = self.__db_table

        self.__lock = srandom.choice(LOCKS)

    def test_raises_with_invalid_lock_type(self):
        with self.assertRaises(ValueError):
            with lock(self.__model, fake.word()):
                'hello'

    def test_starts_a_new_transaction(self):
        with lock(self.__model, self.__lock):
            'hello'
        self.__transaction.atomic.assert_called_once()

    def test_locks_the_table(self):
        cursor = mock.Mock()
        self.__connection.cursor = mock.Mock(return_value=cursor)

        with lock(self.__model, self.__lock):
            'hello'

        cursor.execute.assert_called_once_with(
            'LOCK TABLE %s IN %s MODE' % (self.__db_table, self.__lock)
        )

    def test_runs_the_context(self):
        method = mock.Mock()

        with lock(self.__model, self.__lock):
            method()

        method.assert_called_once()
