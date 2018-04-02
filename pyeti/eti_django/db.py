from contextlib import contextmanager
from django.db import transaction


LOCK_ACCESS_SHARE = 'ACCESS SHARE'
LOCK_ROW_SHARE = 'ROW SHARE'
LOCK_ROW_EXCLUSIVE = 'ROW EXCLUSIVE'
LOCK_SHARE_UPDATE_EXCLUSIVE = 'SHARE UPDATE EXCLUSIVE'
LOCK_SHARE = 'SHARE'
LOCK_SHARE_ROW_EXCLUSIVE = 'SHARE ROW EXCLUSIVE'
LOCK_EXCLUSIVE = 'EXCLUSIVE'
LOCK_ACCESS_EXCLUSIVE = 'ACCESS EXCLUSIVE'
LOCKS = (
    LOCK_ACCESS_SHARE, LOCK_ROW_SHARE, LOCK_ROW_EXCLUSIVE,
    LOCK_SHARE_UPDATE_EXCLUSIVE, LOCK_SHARE, LOCK_SHARE_ROW_EXCLUSIVE,
    LOCK_EXCLUSIVE, LOCK_ACCESS_EXCLUSIVE,
)


@contextmanager
def lock(model, lock_type):
    """
    Decorator or context manager for PostgreSQL's table-level lock functionality.

    Adapted from https://www.caktusgroup.com/blog/2009/05/26/explicit-table-locking-with-postgresql-and-django/.

    Example:
        ```
        from pyeti.eti_django.db import lock, LOCK_ACCESS_EXCLUSIVE

        @lock(MyModel, LOCK_ACCESS_EXCLUSIVE)
        def myfunc()
            ...

        # or

        with lock(MyModel, LOCK_ACCESS_EXCLUSIVE):
            ...
        ```

    PostgreSQL's LOCK Documentation:
    http://www.postgresql.org/docs/latest/interactive/sql-lock.html
    """
    if lock_type not in LOCKS:
        raise ValueError('%s is not a PostgreSQL supported lock mode.')

    with transaction.atomic():
        from django.db import connection
        cursor = connection.cursor()

        cursor.execute('LOCK TABLE %s IN %s MODE' % (model._meta.db_table, lock_type))
        yield
