from contextlib import contextmanager
from django.db import transaction, DatabaseError


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
def db_lock(model, lock):
    if lock not in LOCKS:
        raise ValueError('%s is not a PostgreSQL supported lock mode.')

    with transaction.atomic():
        from django.db import connection
        cursor = connection.cursor()

        try:
            cursor.execute('LOCK TABLE %s IN %s MODE' % (model._meta.db_table, lock))
        except DatabaseError:
            pass

        yield


def require_lock(model, lock):
    """
    Decorator for PostgreSQL's table-level lock functionality

    Copied from https://www.caktusgroup.com/blog/2009/05/26/explicit-table-locking-with-postgresql-and-django/.

    Example:
        @require_lock(MyModel, 'ACCESS EXCLUSIVE')
        def myfunc()
            ...

    PostgreSQL's LOCK Documentation:
    http://www.postgresql.org/docs/latest/interactive/sql-lock.html
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with db_lock(model, lock):
                return func(*args, **kwargs)
        return wrapper
    return decorator
